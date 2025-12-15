import streamlit as st
import utils
from utils import load_css

# Configuration de la page
st.set_page_config(page_title="Recherche par Genre", page_icon="🍿", layout="wide")

# --- Charger le style de la page ---
load_css()

# 1. Chargement des données
df, _ = utils.load_data_and_model()

st.title("🍿 Catalogue par Genres")

if df is not None:
    liste_genres = [
        'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
        'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 
        'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 
        'Thriller', 'War', 'Western'
    ]
    
    # --- DICO LANGUES (Identique à avant) ---
    dico_langues = {
        'de': '🇩🇪 Allemand', 'en': '🇬🇧 Anglais', 'ar': '🇸🇦 Arabe', 'hy': '🇦🇲 Arménien',
        'eu': '🏞️ Basque', 'bs': '🇧🇦 Bosnien', 'cn': '🇭🇰 Cantonais', 'zh': '🇨🇳 Chinois (Mandarin)',
        'ko': '🇰🇷 Coréen', 'hr': '🇭🇷 Croate', 'da': '🇩🇰 Danois', 'es': '🇪🇸 Espagnol',
        'fi': '🇫🇮 Finnois', 'fr': '🇫🇷 Français', 'ka': '🇬🇪 Géorgien', 'he': '🇮🇱 Hébreu',
        'hi': '🇮🇳 Hindi', 'hu': '🇭🇺 Hongrois', 'id': '🇮🇩 Indonésien', 'is': '🇮🇸 Islandais',
        'it': '🇮🇹 Italien', 'ja': '🇯🇵 Japonais', 'ku': '🧣 Kurde', 'lv': '🇱🇻 Letton',
        'mk': '🇲🇰 Macédonien', 'ne': '🇳🇵 Népalais', 'no': '🇳🇴 Norvégien', 'ur': '🇵🇰 Ourdou',
        'fa': '🇮🇷 Persan', 'pl': '🇵🇱 Polonais', 'pt': '🇵🇹 Portugais', 'ro': '🇷🇴 Roumain',
        'ru': '🇷🇺 Russe', 'sr': '🇷🇸 Serbe', 'sv': '🇸🇪 Suédois', 'ta': '🇮🇳 Tamoul',
        'cs': '🇨🇿 Tchèque', 'th': '🇹🇭 Thaïlandais', 'tr': '🇹🇷 Turc', 'uk': '🇺🇦 Ukrainien',
        'vi': '🇻🇳 Vietnamien', 'xx': '❓ Inconnu'
    }

    # Tri intelligent des langues
    codes_bruts = df['Langue Originale'].dropna().unique().tolist()
    liste_codes = sorted(
        codes_bruts,
        key=lambda x: dico_langues.get(x, x).split(' ', 1)[1] if ' ' in dico_langues.get(x, x) else x
    )

    def format_affichage_langue(option):
        if option == "Aucun": return "Indifférent"
        return dico_langues.get(option, option.upper())


    # --- LIGNE 1 : Les 3 Genres (3 colonnes maintenant !) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        # Genre 1 (Obligatoire)
        genre_principal = st.selectbox("Genre 1", liste_genres, index=4)

    with col2:
        # Genre 2 (Exclut le 1)
        liste_2 = [g for g in liste_genres if g != genre_principal]
        genre_secondaire = st.selectbox("Genre 2 (optionnel)", ["Aucun"] + liste_2)

    with col3:
        # Genre 3 (Exclut le 1 ET le 2)
        # On construit la liste des exclus
        exclus = [genre_principal]
        if genre_secondaire != "Aucun":
            exclus.append(genre_secondaire)
            
        liste_3 = [g for g in liste_genres if g not in exclus]
        genre_tertiaire = st.selectbox("Genre 3 (optionnel)", ["Aucun"] + liste_3)

    # --- LIGNE 2 : La Langue ---
    langue_code_selectionne = st.selectbox(
        "Langue originale (optionnel)",
        ["Aucun"] + liste_codes,
        format_func=format_affichage_langue
    )

    # 4. Filtrage en cascade
    films_filtres = df[df[genre_principal] == 1]
    
    if genre_secondaire != "Aucun":
        films_filtres = films_filtres[films_filtres[genre_secondaire] == 1]
        
    if genre_tertiaire != "Aucun":
        films_filtres = films_filtres[films_filtres[genre_tertiaire] == 1]

    if langue_code_selectionne != "Aucun":
        films_filtres = films_filtres[films_filtres['Langue Originale'] == langue_code_selectionne]

    # Tri
    films_filtres = films_filtres.sort_values(by='Popularité', ascending=False)
    
    # Message de résultat dynamique
    msg_genres = f"**{genre_principal}**"
    if genre_secondaire != "Aucun":
        msg_genres += f" + **{genre_secondaire}**"
    if genre_tertiaire != "Aucun":
        msg_genres += f" + **{genre_tertiaire}**"
        
    nom_langue = format_affichage_langue(langue_code_selectionne)
    
    if langue_code_selectionne != "Aucun":
        st.write(f"**{len(films_filtres)}** films trouvés pour {msg_genres} (Langue : **{nom_langue}**)")
    else:
        st.write(f"**{len(films_filtres)}** films trouvés pour {msg_genres}")
        
    st.markdown("---")

    # 5. Affichage
    cols = st.columns(5)
    
    # Sécurité : ne pas planter si on a moins de 5 films
    nb_films_a_afficher = min(5, len(films_filtres))
    
    for index, (i, film) in enumerate(films_filtres.head(5).iterrows()):
        col = cols[index % 5]
        with col:
            url_affiche = film['Affiche du Film']
            if isinstance(url_affiche, str) and "http" in url_affiche:
                st.image(url_affiche, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x450?text=No+Image", use_container_width=True)
            
            st.caption(f"**{film['Titre']}**")

else:
    st.error("Impossible de charger les données.")