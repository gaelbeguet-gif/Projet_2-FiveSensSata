import streamlit as st
import pandas as pd
import logging
from utils import load_css, load_data_and_films, display_movies_grid, get_film_suggestions, recommandation_films, display_movie_details

# Configuration
st.set_page_config(page_title="Moteur - Senechal Movie", page_icon="🔍", layout="wide")

# Chargement style
load_css()

# Logging
logger = logging.getLogger(__name__)

# Chargement données
try:
    df_films, df_scaler = load_data_and_films()
    logger.info("✅ Données chargées (page moteur)")
except Exception as e:
    st.error(f"❌ Erreur chargement données: {e}")
    st.stop()

# === TITRE ===
st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h1 style="color: #FF4D7D; font-size: 2.5em; margin: 0;">🔍 Moteur de Recommandation</h1>
        <p style="color: #E0E0E0; font-size: 1.1em; margin-top: 10px;">
            Cherchez un film et découvrez des recommandations personnalisées
        </p>
    </div>
    <hr style="border-color: #FF4D7D; margin: 20px 0;">
""", unsafe_allow_html=True)

# === RECHERCHE FILM ===
search_query = st.text_input(
    "🎬 Cherchez un film",
    placeholder="Tapez au moins 2 caractères...",
    label_visibility="collapsed"
)

selected_film = None
film_row = None

if search_query and len(search_query) >= 2:
    try:
        # Autocomplete suggestions
        suggestions = get_film_suggestions(search_query)
        
        if suggestions:
            selected_film = st.selectbox(
                "Films trouvés:",
                suggestions,
                label_visibility="collapsed"
            )
            
            # Récupérer les détails
            film_row = df_films[df_films['Titre'] == selected_film].iloc[0]
            
        else:
            st.info("💡 Aucun film trouvé. Essayez une autre recherche.")
            logger.warning(f"Aucun film trouvé pour: {search_query}")
            
    except Exception as e:
        st.error(f"❌ Erreur recherche: {e}")
        logger.error(f"Erreur recherche film: {e}")

elif search_query and len(search_query) < 2:
    st.info("💡 Tapez au moins 2 caractères pour rechercher...")

# === AFFICHAGE DÉTAILS & RECOMMANDATIONS ===
if film_row is not None:
    st.markdown("---")
    
    try:
        # Détails du film
        display_movie_details(film_row)
        
        # Recommandations KNN
        st.markdown("""
            <div style="margin-top: 40px;">
                <h3 style="color: #FF4D7D;">🎥 Films similaires</h3>
                <hr style="border-color: #FF4D7D; margin: 10px 0;">
            </div>
        """, unsafe_allow_html=True)
        
        # Slider nombre de recommandations
        n_reco = st.slider(
            "Nombre de films à afficher",
            min_value=1,
            max_value=10,
            value=5,
            step=1
        )
        
        # Recommandations
        reco_df = recommandation_films(selected_film, n_reco=10)
        display_movies_grid(reco_df.head(n_reco), cols_per_row=5)
        
        logger.info(f"✅ Recommandations affichées pour: {selected_film}")
        
    except Exception as e:
        st.error(f"❌ Erreur affichage recommandations: {e}")
        logger.error(f"Erreur recommandations: {e}")

st.markdown("\n" * 3)
