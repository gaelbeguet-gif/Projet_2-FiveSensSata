import streamlit as st
import base64
import os
import pandas as pd
# On suppose que tu as créé le fichier utils.py comme suggéré précédemment
from utils import load_css 

# --- CONFIGURATION INITIALE ---
st.set_page_config(
    page_title="Senechal Movie",
    page_icon="🎬",
    layout="wide"
)

# --- CHARGEMENT DU STYLE GLOBAL ---
# Charge le CSS de base (celui généré à l'étape précédente)
load_css()

# --- GESTION DE L'IMAGE DE FOND ---
def get_img_as_base64(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

current_dir = os.path.dirname(os.path.abspath(__file__))
# Assure-toi que le nom du fichier est exact
image_path = os.path.join(current_dir, "bandeau_senechal.png") 
img = get_img_as_base64(image_path)

# --- STYLE SPÉCIFIQUE (SURCHARGE) ---
# On adapte le CSS pour coller à l'identité visuelle de ton image (Rose/Noir/Police Serif)
st.markdown(f"""
    <style>
    /* Image de fond en haut de page */
    .stApp {{
        background-image: url("data:image/png;base64,{img}");
        background-size: 100% auto;
        background-position: top center;
        background-repeat: no-repeat;
        /* On descend le contenu pour ne pas cacher le bandeau image */
        padding-top: 150px; 
    }}
    
    /* Ajustement du conteneur principal */
    .block-container {{
        padding-top: 2rem;
        margin-top: 80px; /* Espace pour laisser voir le titre de l'image si besoin */
    }}

    /* POLICE DU TITRE (Style SENECHAL) */
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,700&display=swap');
    
    .titre-cinema {{
        font-family: 'Bodoni Moda', 'Didot', serif;
        font-size: 80px;
        color: white;
        line-height: 0.8;
        text-transform: uppercase;
        margin-bottom: 0px;
    }}
    
    .sous-titre-cinema {{
        font-family: 'Bodoni Moda', serif;
        font-size: 80px;
        font-weight: 400; /* Plus fin comme sur l'image */
        color: white;
    }}

    /* NAVIGATION - BOUTONS */
    /* On surcharge le style des boutons pour qu'ils ressemblent à des onglets de ticket */
    div.stButton > button {{
        background-color: #1a1a1a;
        color: white;
        border: 2px solid #eb4d6d; /* Le rose du ticket */
        border-radius: 0px; /* Carrés */
        height: 60px;
        width: 100%;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s;
    }}

    div.stButton > button:hover {{
        background-color: #eb4d6d; /* Fond rose au survol */
        color: white;
        box-shadow: 0 0 15px #eb4d6d;
        transform: translateY(-2px);
        border: 2px solid #eb4d6d;
    }}

    /* Active State (si possible en CSS pur, sinon géré par logique Python) */
    div.stButton > button:active {{
        background-color: white;
        color: black;
    }}
    
    /* Masquer le menu hamburger par défaut pour le style */
    #MainMenu {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)


# --- INITIALISATION SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "accueil"

# --- ENTÊTE & NAVIGATION ---
# On utilise des colonnes pour placer le titre (si tu veux le réécrire) et le menu
col_titre, col_nav = st.columns([1, 2])

with col_titre:
    # Optionnel : Si l'image contient déjà le texte, tu peux laisser vide ou ajouter un titre invisible pour le SEO
    # Ici, je recrée le style texte pour l'exemple
    st.markdown('<div class="titre-cinema">SENECHAL<br><span class="sous-titre-cinema">MOVIE</span></div>', unsafe_allow_html=True)

st.markdown("---")

# --- MENU DE NAVIGATION ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    # Si on clique, on va vers le fichier dans pages/1_recommandation.py
    if st.button("🍿 RECOMMANDATION"):
        st.switch_page("pages/2_recommandations.py")

with m2:
    if st.button("🎥 TRAILERS"):
        st.switch_page("pages/3_video.py")

with m3:
    if st.button("🏷️ PAR GENRE"):
        st.switch_page("pages/4_genres.py")

with m4:
    if st.button("⭐ ACTEURS"):
        st.switch_page("pages/5_acteurs.py")


# --- ROUTAGE DES PAGES ---
# C'est ici que le contenu change sans recharger toute l'application

if st.session_state.page == "accueil":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Bienvenue au Cinéma Sénéchal</h2>", unsafe_allow_html=True)
    st.info("Sélectionnez une option dans le menu ci-dessus pour commencer.")

elif st.session_state.page == "reco":
    st.markdown("### 🍿 Moteur de Recommandation")
    # --- ICI TU COLLES LA LOGIQUE DE RECOMMANDATION (INPUT, ETC) ---
    search = st.text_input("Quel film avez-vous aimé ?", placeholder="Ex: Avatar")
    if search:
        st.success(f"Recherche lancée pour : {search} (Intégrez votre fonction reco ici)")
        # Exemple d'affichage dummy
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.image("https://via.placeholder.com/300x450?text=Film", use_container_width=True)
                st.caption(f"Film suggéré {i+1}")

elif st.session_state.page == "trailer":
    st.markdown("### 🎥 Salle de Projection")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Exemple RickRoll

elif st.session_state.page == "genre":
    st.markdown("### 🏷️ Sélection par Genre")
    genres = ["Action", "Comédie", "Drame", "Sci-Fi", "Horreur"]
    selected_genre = st.selectbox("Choisissez votre ambiance :", genres)
    st.write(f"Affichage des films de type : **{selected_genre}**")

elif st.session_state.page == "acteurs":
    st.markdown("### ⭐ Fiches Acteurs & Actrices")
    c1, c2 = st.columns(2)
    with c1:
        st.image("https://via.placeholder.com/150", width=150)
        st.write("**Nom Acteur**")
        st.write("Biographie courte...")
    with c2:
        st.image("https://via.placeholder.com/150", width=150)
        st.write("**Nom Actrice**")
        st.write("Biographie courte...")

# --- PIED DE PAGE ---
st.markdown('<div class="seats-footer"></div>', unsafe_allow_html=True)