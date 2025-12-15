import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors

# Liste des colonnes de métadonnées à exclure pour la matrice X (car ce n'est pas du numérique utile au modèle)
METADATA_COLS = [
    'tconst', 'Id_TMDB', 'Titre', 'Titre Original', 'Résumé', 
    'Lien_vidéo', 'Affiche du Film', 'Logo', 'Langue Originale'
]

@st.cache_resource
def load_data_and_model():
    """
    Charge les données, prépare la matrice X et entraîne le modèle.
    Mis en cache pour ne pas recharger à chaque clic.
    """
    # 1. Chargement du CSV traité
    try:
        df = pd.read_csv("data\df_films_scaler.csv")
    except FileNotFoundError:
        st.error("Le fichier 'df_films_scaler.csv' est introuvable. Place-le dans le même dossier que ce script.")
        return None, None

    # 2. Reconstruction de la colonne 'Genres_str' pour l'affichage (optionnel mais utile)
    # On récupère les colonnes de genres qui sont à 1
    genre_cols = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
                  'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 
                  'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
    
    # Petite fonction pour lister les genres d'un film
    def get_genres(row):
        return [g for g in genre_cols if row.get(g, 0) == 1]

    df['Genres_List'] = df.apply(get_genres, axis=1)
    
    # 3. Préparation de la matrice X (Feature Engineering)
    # On garde tout sauf les métadonnées pour le calcul de distance
    # Assurons-nous que toutes les colonnes restantes sont numériques
    X = df.drop(columns=[c for c in METADATA_COLS if c in df.columns], errors='ignore')
    
    # On retire aussi la colonne 'Genres_List' qu'on vient de créer car elle n'est pas numérique
    X = X.select_dtypes(include=['number'])
    
    # 4. Entraînement du Modèle
    model = NearestNeighbors(n_neighbors=6).fit(X)
    
    return df, model

# Fonction de recommandation utilisable partout
def get_recommendations(df, model, film_title):
    if film_title not in df['Titre'].values:
        return None
    
    # Récupérer l'index du film
    idx = df[df['Titre'] == film_title].index[0]
    
    # On doit reconstruire le vecteur X pour ce film spécifique pour interroger le modèle
    # On refait la même sélection que lors de l'entraînement
    row_data = df.iloc[[idx]].drop(columns=[c for c in METADATA_COLS if c in df.columns], errors='ignore')
    row_vector = row_data.select_dtypes(include=['number'])
    
    distances, indices = model.kneighbors(row_vector)
    
    # On ignore le premier (le film lui-même)
    reco_indices = indices[0][1:]
    
    return df.iloc[reco_indices]

# utils.py
import streamlit as st

def load_css():
    with open("assets/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# ============================================================================

"""
UTILS.PY - Module utilitaire pour Senechal Movie
Contient toutes les fonctions partagées entre les pages
"""

import pandas as pd
import streamlit as st
import logging
from fuzzywuzzy import fuzz
from sklearn.neighbors import NearestNeighbors
import os

# Configuration logging
logger = logging.getLogger(__name__)

# Liste des colonnes de métadonnées à exclure
METADATA_COLS = [
    'tconst', 'Id_TMDB', 'Titre', 'Titre Original', 'Résumé',
    'Lien_vidéo', 'Affiche du Film', 'Logo', 'Langue Originale'
]

# Genre columns
GENRE_COLS = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror',
    'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport',
    'Thriller', 'War', 'Western'
]

# ============================================================================
# 1. CHARGEMENT CSS
# ============================================================================

def load_css():
    """Charge le fichier CSS personnalisé"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(current_dir, "assets", "style.css")
        
        if os.path.exists(css_path):
            with open(css_path) as f:
                css_content = f.read()
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
            logger.info("✅ CSS chargé")
        else:
            logger.warning(f"⚠️ CSS non trouvé à {css_path}")
            
    except Exception as e:
        logger.error(f"❌ Erreur chargement CSS: {e}")

# ============================================================================
# 2. CHARGEMENT DONNÉES
# ============================================================================

@st.cache_resource
def load_data_and_films():
    """
    Charge les données films avec cache Streamlit
    Retourne: (df_films, df_scaler)
    """
    try:
        # Chemin relatif correct
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "data", "films.csv")
        
        if not os.path.exists(csv_path):
            st.error(f"❌ Fichier 'films.csv' non trouvé à {csv_path}")
            logger.error(f"Fichier manquant: {csv_path}")
            return None, None
        
        df_films = pd.read_csv(csv_path)
        logger.info(f"✅ {len(df_films)} films chargés")
        
        # Créer colonne genres list
        df_films['Genres_List'] = df_films.apply(
            lambda row: [g for g in GENRE_COLS if row.get(g, 0) == 1],
            axis=1
        )
        
        return df_films, None
        
    except Exception as e:
        st.error(f"❌ Erreur chargement données: {e}")
        logger.error(f"Erreur load_data_and_films: {e}")
        return None, None

# ============================================================================
# 3. AFFICHAGE GRILLE FILMS
# ============================================================================

def display_movies_grid(df, cols_per_row=5):
    """
    Affiche les films en grille responsive
    ⚠️ IMPORTANT: utilise use_container_width (pas use_column_width déprécié)
    """
    try:
        if df is None or len(df) == 0:
            st.info("💡 Aucun film à afficher")
            return
        
        # Calculer nombre de lignes
        n_films = len(df)
        n_rows = (n_films + cols_per_row - 1) // cols_per_row
        
        # Afficher par lignes
        for row_idx in range(n_rows):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                film_idx = row_idx * cols_per_row + col_idx
                
                if film_idx < n_films:
                    film = df.iloc[film_idx]
                    
                    with cols[col_idx]:
                        # Image affiche
                        try:
                            poster_url = film.get('Affiche du Film', '')
                            if isinstance(poster_url, str) and 'http' in poster_url:
                                st.image(
                                    poster_url,
                                    use_container_width=True  # ✅ CORRECT (pas use_column_width)
                                )
                            else:
                                st.image(
                                    "https://via.placeholder.com/300x450?text=No+Image",
                                    use_container_width=True  # ✅ CORRECT
                                )
                        except Exception as e:
                            logger.warning(f"Image error pour {film.get('Titre', 'Unknown')}: {e}")
                        
                        # Titre
                        titre = film.get('Titre', 'Sans titre')
                        st.markdown(f"**{titre}**", unsafe_allow_html=True)
                        
                        # Infos supplémentaires
                        try:
                            note = film.get('Moyenne des votes', 0)
                            annee = film.get('Année de Sortie', 'N/A')
                            st.caption(f"⭐ {note:.1f} | {annee}")
                        except Exception as e:
                            logger.warning(f"Infos error pour {titre}: {e}")
        
        logger.info(f"✅ Grille {n_films} films affichée")
        
    except Exception as e:
        st.error(f"❌ Erreur affichage grille: {e}")
        logger.error(f"Erreur display_movies_grid: {e}")

# ============================================================================
# 4. RECHERCHE AUTOCOMPLETE
# ============================================================================

def get_film_suggestions(query, max_suggestions=10):
    """
    Retourne suggestions de films basé sur fuzzy matching
    """
    try:
        df_films, _ = load_data_and_films()
        
        if df_films is None:
            return []
        
        # Normaliser query
        query_norm = query.lower().strip()
        
        # Fuzzy match sur titres
        titres = df_films['Titre'].tolist()
        
        suggestions = []
        for titre in titres:
            score = fuzz.token_set_ratio(query_norm, titre.lower())
            if score >= 60:  # Cutoff 60%
                suggestions.append((titre, score))
        
        # Trier par score descendant
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner top N titres
        result = [s[0] for s in suggestions[:max_suggestions]]
        
        logger.info(f"✅ {len(result)} suggestions pour '{query}'")
        return result
        
    except Exception as e:
        logger.error(f"Erreur get_film_suggestions: {e}")
        return []

# ============================================================================
# 5. RECOMMANDATIONS KNN
# ============================================================================

def recommandation_films(titre_film, n_reco=10):
    """
    Retourne N films similaires basé sur KNN
    """
    try:
        df_films, _ = load_data_and_films()
        
        if df_films is None or titre_film not in df_films['Titre'].values:
            logger.warning(f"Film non trouvé: {titre_film}")
            return pd.DataFrame()
        
        # Récupérer index du film
        idx_film = df_films[df_films['Titre'] == titre_film].index[0]
        
        # Préparer features (tout sauf métadonnées)
        features = [col for col in df_films.columns if col not in METADATA_COLS and col != 'Genres_List']
        X = df_films[features].fillna(0)
        
        # Entraîner KNN
        model = NearestNeighbors(n_neighbors=n_reco+1, algorithm='auto')
        model.fit(X)
        
        # Trouver voisins
        distances, indices = model.kneighbors(X.iloc[[idx_film]])
        
        # Exclure le film lui-même (premier résultat)
        indices_reco = indices[0][1:]
        
        reco_df = df_films.iloc[indices_reco].copy()
        
        logger.info(f"✅ {len(reco_df)} recommandations pour '{titre_film}'")
        return reco_df
        
    except Exception as e:
        logger.error(f"Erreur recommandation_films: {e}")
        return pd.DataFrame()

# ============================================================================
# 6. AFFICHAGE DÉTAILS FILM
# ============================================================================

def display_movie_details(film_row):
    """
    Affiche les détails complets d'un film
    """
    try:
        titre = film_row.get('Titre', 'Sans titre')
        titre_original = film_row.get('Titre Original', titre)
        duree = film_row.get('Durée (minutes)', 'N/A')
        annee = film_row.get('Année de Sortie', 'N/A')
        note = film_row.get('Moyenne des votes', 0)
        resume = film_row.get('Résumé', 'Pas de résumé')
        genres = film_row.get('Genres_List', [])
        
        # Afficher en colonnes
        col1, col2 = st.columns([2, 3])
        
        with col1:
            poster_url = film_row.get('Affiche du Film', '')
            if isinstance(poster_url, str) and 'http' in poster_url:
                st.image(poster_url, use_container_width=True)  # ✅ CORRECT
            else:
                st.image("https://via.placeholder.com/300x450?text=No+Image", use_container_width=True)  # ✅ CORRECT
        
        with col2:
            st.markdown(f"""
                <div style="background-color: rgba(255, 77, 125, 0.1); 
                            border: 2px solid #FF4D7D; 
                            border-radius: 12px; 
                            padding: 20px;">
                    <h2 style="color: #FF4D7D; margin-top: 0;">{titre}</h2>
                    <p style="color: #E0E0E0;"><strong>Titre original:</strong> {titre_original}</p>
                    <p style="color: #E0E0E0;"><strong>Année:</strong> {annee}</p>
                    <p style="color: #E0E0E0;"><strong>Durée:</strong> {duree} minutes</p>
                    <p style="color: #FF4D7D;"><strong>Note:</strong> ⭐ {note:.1f}/10</p>
                    <p style="color: #E0E0E0;"><strong>Genres:</strong> {', '.join(genres)}</p>
                    <hr style="border-color: #FF4D7D;">
                    <p style="color: #FFFFFF;">{resume}</p>
                </div>
            """, unsafe_allow_html=True)
        
        logger.info(f"✅ Détails affichés pour '{titre}'")
        
    except Exception as e:
        logger.error(f"Erreur display_movie_details: {e}")
        st.warning("Erreur affichage détails film")

# ============================================================================
# 7. UTILITAIRES
# ============================================================================

def normalize_text(text):
    """Normalise texte (minuscules, accents, etc.)"""
    import unicodedata
    text = str(text).lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')
    return text

# ============================================================================
# 8. INITIALISATIONS
# ============================================================================

def initialize_session_state():
    """Initialise session state Streamlit"""
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    logger.info("✅ Session state initialisée")

if __name__ == "__main__":
    logger.info("Module utils.py chargé")

@st.cache_resource
def load_data_and_model():
    """
    Charge les données, prépare la matrice X et entraîne le modèle.
    Mis en cache pour ne pas recharger à chaque clic.
    """
    # 1. Chargement du CSV traité
    try:
        df = pd.read_csv("data\df_films_scaler.csv")
    except FileNotFoundError:
        st.error("Le fichier 'df_films_scaler.csv' est introuvable. Place-le dans le même dossier que ce script.")
        return None, None

    # 2. Reconstruction de la colonne 'Genres_str' pour l'affichage (optionnel mais utile)
    # On récupère les colonnes de genres qui sont à 1
    genre_cols = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
                  'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 
                  'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
    
    # Petite fonction pour lister les genres d'un film
    def get_genres(row):
        return [g for g in genre_cols if row.get(g, 0) == 1]

    df['Genres_List'] = df.apply(get_genres, axis=1)
    
    # 3. Préparation de la matrice X (Feature Engineering)
    # On garde tout sauf les métadonnées pour le calcul de distance
    # Assurons-nous que toutes les colonnes restantes sont numériques
    X = df.drop(columns=[c for c in METADATA_COLS if c in df.columns], errors='ignore')
    
    # On retire aussi la colonne 'Genres_List' qu'on vient de créer car elle n'est pas numérique
    X = X.select_dtypes(include=['number'])
    
    # 4. Entraînement du Modèle
    model = NearestNeighbors(n_neighbors=6).fit(X)
    
    return df, model