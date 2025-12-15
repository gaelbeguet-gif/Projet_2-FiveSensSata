import streamlit as st
import pandas as pd
import logging
from utils import load_css, load_data_and_films, display_movies_grid

# Configuration
st.set_page_config(page_title="Accueil - Senechal Movie", page_icon="🏠", layout="wide")

# Chargement style
load_css()

# Logging
logger = logging.getLogger(__name__)

# Chargement données
try:
    df_films, df_scaler = load_data_and_films()
    logger.info("✅ Données chargées (page accueil)")
except Exception as e:
    st.error(f"❌ Erreur chargement données: {e}")
    st.stop()

# === TITRE PRINCIPAL ===
st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h1 style="color: #FF4D7D; font-size: 3em; margin: 0;">🎬 Senechal Movie</h1>
        <p style="color: #E0E0E0; font-size: 1.2em; margin-top: 10px;">
            Découvrez les films qui vous passionnent
        </p>
    </div>
    <hr style="border-color: #FF4D7D; margin: 20px 0;">
""", unsafe_allow_html=True)

# === 4 MÉTRIQUES PRINCIPALES ===
col1, col2= st.columns(2)

try:
    with col1:
        st.metric("🎥 Films", f"{len(df_films):,}")
    
    
    with col2:
        note_moy = df_films['Moyenne des votes'].mean()
        st.metric("⭐ Note Moyenne", f"{note_moy:.1f}/10")
    
    
    logger.info("✅ Métriques affichées")
    
except Exception as e:
    st.error(f"❌ Erreur affichage métriques: {e}")
    logger.error(f"Erreur métriques: {e}")

# === TOP 10 FILMS ===
st.markdown("""
    <div style="margin-top: 40px;">
        <h2 style="color: #FF4D7D; text-align: center;">🏆 Top 10 Films les mieux notés</h2>
        <hr style="border-color: #FF4D7D; margin: 20px 0;">
    </div>
""", unsafe_allow_html=True)

try:
    top_10 = df_films.nlargest(10, 'Moyenne des votes')
    display_movies_grid(top_10, cols_per_row=5)
    logger.info("✅ Top 10 films affichés")
    
except Exception as e:
    st.error(f"❌ Erreur affichage top 10: {e}")
    logger.error(f"Erreur top 10: {e}")

# === SECTION INFORMATIONS ===
st.markdown("""
    <div style="margin-top: 60px; padding: 30px; background-color: rgba(255, 77, 125, 0.1); 
                border: 2px solid #FF4D7D; border-radius: 12px;">
        <h3 style="color: #FF4D7D; margin-top: 0;">💡 Comment utiliser Senechal Movie?</h3>
        <ul style="color: #E0E0E0; line-height: 1.8;">
            <li><strong>🔍 Moteur:</strong> Cherchez un film et découvrez des recommandations basées sur la similarité</li>
            <li><strong>🎬 Genres:</strong> Filtrez par genres multiples pour trouver votre film idéal</li>
            <li><strong>🎭 Acteurs:</strong> Explorez la filmographie de vos acteurs préférés</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

st.markdown("\n")
