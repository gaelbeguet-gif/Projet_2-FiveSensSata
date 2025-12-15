import streamlit as st
import pandas as pd


# --- GESTION DES IMPORTS ET DONNÉES DE SECOURS ---
try:
    from reco import suggerer_titres, recommandation_films
except ImportError:
    # Fallback enrichi pour que les détails (Budget, Trailer) fonctionnent sans le backend
    def suggerer_titres(t): 
        return ["Titanic", "Avatar", "Inception"] if t else []
    
    def recommandation_films(t, n_reco=5): 
        return pd.DataFrame({
            "Titre": [f"Film Similaire {i}" for i in range(1, 6)],
            "Affiche du Film": ["https://via.placeholder.com/300x450?text=Affiche"] * 5,
            "Budget": ["100M$", "250M$", "50M$", "15M$", "200M$"],
            "Overview": ["Ceci est un résumé fictif pour tester l'affichage des détails du film."]*5,
            "Trailer": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]*5
        })


# --- CHARGEMENT DES DONNÉES (optionnel, avec cache) ---
@st.cache_data
def charger_donnees_films():
    """Charge les données depuis un CSV ou retourne None si non disponible"""
    try:
        df = pd.read_csv("data/films.csv")
        df['Lien_vidéo'] = df['Lien_vidéo'].fillna('')
        df['Affiche du Film'] = df['Affiche du Film'].fillna('')
        df['Résumé'] = df['Résumé'].fillna("Pas de résumé disponible.")
        return df
    except FileNotFoundError:
        return None


# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Ciné Recommandation",
    layout="wide",
    page_icon="🎬"
)


# --- INJECTION CSS (Le "Pimping") ---
st.markdown("""
    <style>
    /* 1. FOND DE SCENE (RIDEAUX) */
    .stApp {
        background-color: #1a1a1a;
        background-image: linear-gradient(
            90deg, 
            #4b0082 0%, #800080 10%,
            #000000 20%, #000000 80%,
            #800080 90%, #4b0082 100%
        );
        color: white;
    }
    /* 2. FORCER LES TEXTES EN BLANC/CLAIR */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #e0e0e0;
    }

    /* 2. LE PANNEAU ROSE (TITRE) */
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 40px;
        padding-top: 20px;
    }
    .pink-title-box {
        background-color: #dda0dd;
        border-radius: 20px;
        padding: 15px 40px;
        box-shadow: 0px 0px 20px rgba(221, 160, 221, 0.6);
        text-align: center;
        color: #2c003e !important;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 2em;
        border: 2px solid #fff;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    /* 3. STYLISATION DES WIDGETS */
    .stTextInput input {
        color: white !important;
        background-color: #333 !important;
    }
    .stTextInput > div > div > input {
        text-align: center;
        background-color: #2c003e;
        color: white;
        border: 1px solid #dda0dd;
    }
    .stSelectbox > div > div {
        background-color: #2c003e;
        color: white;
    }
    /* Boutons personnalisés */
    .stButton > button {
        background-color: #dda0dd;
        color: #2c003e !important;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        border: none;
    }
    .stButton > button:hover {
        background-color: #fff;
        color: #purple;
    }

    /* 4. CADRES DES AFFICHES ET DETAILS */
    img {
        border-radius: 5px;
        box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }
    img:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 25px rgba(255, 215, 0, 0.6);
    }
    
    /* Boite de détails du film sélectionné */
    .movie-details-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #dda0dd;
        margin-top: 20px;
    }

    /* 5. LES SIEGES (FOOTER) */
    .seats-footer {
        position: fixed; left: 0; bottom: 0; width: 100%; height: 60px; z-index: 100;
        background-image: radial-gradient(circle at 50% 60%, #5e2a84 30px, transparent 31px);
        background-size: 70px 80px; background-repeat: repeat-x; pointer-events: none;
    }
    
    /* Masquer menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# --- INITIALISATION DE SESSION STATE ---
if 'page_actuelle' not in st.session_state:
    st.session_state['page_actuelle'] = 'recherche'

if 'film_selectionne' not in st.session_state:
    st.session_state['film_selectionne'] = None

if 'suggestions' not in st.session_state:
    st.session_state['suggestions'] = []

if 'df_reco' not in st.session_state:
    st.session_state['df_reco'] = pd.DataFrame()

if 'last_source' not in st.session_state:
    st.session_state['last_source'] = None

if 'liste_titres_brut' not in st.session_state:
    st.session_state['liste_titres_brut'] = ""

if 'selected_movie_title' not in st.session_state:
    st.session_state['selected_movie_title'] = None

if 'run_reco' not in st.session_state:
    st.session_state['run_reco'] = False

if 'trailer_url' not in st.session_state:
    st.session_state['trailer_url'] = ""


# --- FONCTIONS DE NAVIGATION ---
def aller_au_trailer(url):
    """Navigue vers la page de lecture vidéo"""
    st.session_state['trailer_url'] = url
    st.session_state['page_actuelle'] = 'trailer'
    st.rerun()


def retour_recherche():
    """Retour à la page de recherche"""
    st.session_state['page_actuelle'] = 'recherche'
    st.rerun()


def selectionner_film(film):
    """Callback pour sélectionner un film (utilisé avec on_click)"""
    st.session_state['film_selectionne'] = film


def lancer_recommandations(titre_choisi):
    """Callback pour lancer les recommandations"""
    st.session_state['run_reco'] = True
    st.session_state['selected_movie_title'] = titre_choisi
    st.session_state['film_selectionne'] = None


# =========================================================
# VUE 1 : RECHERCHE ET RECOMMANDATION
# =========================================================
if st.session_state['page_actuelle'] == 'recherche':

    # 1. Le Titre façon panneau rose
    st.markdown("""
        <div class="header-container">
            <div class="pink-title-box">
                <span>🎬</span>
                <span>RECOMMANDATION DE FILMS</span>
                <span>🍿</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Zone de recherche avec liste manuelle + CSV optionnel
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("#### 📋 Liste de films à explorer")
        
        # Option 1 : Chargement depuis CSV
        df_films = charger_donnees_films()
        titres_csv = []
        if df_films is not None:
            titres_csv = df_films['Titre'].unique().tolist()
        
        # Option 2 : Saisie manuelle
        st.markdown("*Ou entrez vos titres (un par ligne) :*")
        liste_saisie = st.text_area(
            "Titres manuels :",
            value=st.session_state.get("liste_titres_brut", ""),
            height=100,
            label_visibility="collapsed"
        )
        st.session_state["liste_titres_brut"] = liste_saisie
        
        # Fusion : titres du CSV + titres manuels
        titres_manuel = [l.strip() for l in liste_saisie.split("\n") if l.strip()]
        titres_complets = list(dict.fromkeys(titres_csv + titres_manuel))  # Fusion sans doublon
        
        # Selectbox déroulant
        titre_saisi = st.selectbox(
            "Quel film avez-vous aimé ?",
            options=titres_complets if titres_complets else ["Aucun film disponible"],
            index=None,
            placeholder="Tapez ou choisissez un film..."
        )

        # Bouton de recherche
        if st.button("🔎 Chercher le film", use_container_width=True):
            if not titre_saisi or titre_saisi == "Aucun film disponible":
                st.warning("Merci de saisir ou sélectionner un titre de film.")
            else:
                suggestions = suggerer_titres(titre_saisi)
                if not suggestions:
                    st.info("Aucun film ne correspond à cette saisie.")
                else:
                    st.session_state["suggestions"] = suggestions
                    st.session_state.pop("film_selectionne", None)

    # 3. Zone de sélection du film de départ
    if st.session_state["suggestions"]:
        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c2:
            titre_choisi = st.selectbox(
                "Confirmez votre film de départ :",
                st.session_state["suggestions"],
                key="select_titre_choisi"
            )

            if st.button("✨ Lancer les recommandations ✨", use_container_width=True):
                lancer_recommandations(titre_choisi)

        # 4. Affichage des résultats
        if st.session_state.get("run_reco"):
            film_source = st.session_state["selected_movie_title"]
            
            # Cache du dataframe pour performances
            if "df_reco" not in st.session_state or st.session_state.get("last_source") != film_source:
                st.session_state["df_reco"] = recommandation_films(film_source, n_reco=5)
                st.session_state["last_source"] = film_source
            
            df_reco = st.session_state["df_reco"]

            st.markdown(
                f"<h3 style='text-align: center; color: #dda0dd;'>Films recommandés si vous avez aimé : "
                f"<i>{film_source}</i></h3>",
                unsafe_allow_html=True
            )
            st.write("")

            if df_reco.empty:
                st.info("Pas de recommandations trouvées")
            else:
                n_cols = min(len(df_reco), 5)
                cols = st.columns(n_cols)

                # Boucle d'affichage avec callback on_click
                for col, (_, film) in zip(cols, df_reco.iterrows()):
                    with col:
                        # Image
                        try:
                            image_url = film.get("Affiche du Film", "")
                            if not isinstance(image_url, str) or len(image_url) < 5:
                                image_url = "https://via.placeholder.com/300x450?text=No+Image"
                            st.image(image_url, use_container_width=True)
                        except:
                            st.image("https://via.placeholder.com/300x450?text=Erreur", use_container_width=True)

                        # Titre
                        st.markdown(
                            f"<div style='text-align:center; font-weight:bold; "
                            f"color: #e0e0e0; margin-top: 5px; height: 50px;'>{film['Titre']}</div>",
                            unsafe_allow_html=True
                        )

                        # Bouton "Voir la fiche" avec callback
                        st.button(
                            "Voir la fiche",
                            key=f"btn_{film['Titre']}_{id(film)}",
                            on_click=selectionner_film,
                            args=(film,),
                            use_container_width=True
                        )

    # 5. Zone de DÉTAILS (Apparaît au clic)
    if st.session_state["film_selectionne"] is not None:
        sel_film = st.session_state["film_selectionne"]

        st.markdown("---")
        st.markdown(
            f"<h2 style='text-align:center; color:#dda0dd !important;'>Détails : {sel_film['Titre']}</h2>",
            unsafe_allow_html=True
        )

        # Conteneur stylisé
        st.markdown('<div class="movie-details-box">', unsafe_allow_html=True)

        d_col1, d_col2 = st.columns([1, 3])
        
        with d_col1:
            # Ré-affichage de l'image en petit
            img_url = sel_film.get("Affiche du Film", "https://via.placeholder.com/300x450")
            st.image(img_url, use_container_width=True)

        with d_col2:
            # Récupération sécurisée des infos
            budget = sel_film.get("Budget", "Non renseigné")
            resume = sel_film.get("Overview", "Pas de résumé disponible.")
            trailer = sel_film.get("Trailer", "")

            st.markdown(f"**💰 Budget :** {budget}")
            st.markdown("**📝 Résumé :**")
            st.write(resume)

            st.markdown("<br>", unsafe_allow_html=True)

            # Bouton Trailer
            if st.button("🎥 Voir la Bande Annonce (Interne)", use_container_width=True):
                aller_au_trailer(trailer)

        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# VUE 2 : LECTEUR VIDEO (TRAILER)
# =========================================================
elif st.session_state['page_actuelle'] == 'trailer':

    if st.button("⬅️ Retour aux recommandations", use_container_width=True):
        retour_recherche()

    st.markdown("""
        <div class="header-container">
            <div class="pink-title-box">
                <span>🎥</span>
                <span>SALLE DE PROJECTION</span>
                <span>🍿</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_v_1, col_v_2, col_v_3 = st.columns([1, 4, 1])
    with col_v_2:
        url = st.session_state.get('trailer_url', '')
        if url:
            st.video(url)
        else:
            st.warning("Désolé, lien vidéo introuvable.")


# --- PIED DE PAGE (Les Sièges) ---
st.markdown('<div class="seats-footer"></div>', unsafe_allow_html=True)
