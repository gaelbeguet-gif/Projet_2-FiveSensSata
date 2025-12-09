# Dans le terminal:
# pip install streamlit streamlit_authentificator streamlit_option_menu
# Pour lancer dans l'application web : streamlit run current_projet_2.py
import streamlit as st
import numpy as np
import pandas as pd
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
import os.path

# --- Configuration de la page (Doit être la première commande Streamlit) ---
# Page web : https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config

st.set_page_config(
    page_title="Ciné Recommandation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fonctions pour chaque page ---
def page_accueil():
    st.title("Sénéchal Movie 🎬")
    st.write("Contenu de la page d'accueil...")
    # Ici, nous mettrons le HTML/CSS pour le fond plus tard

def page_recommandation():
    st.title("Recommandation de films 🤖")
    st.write("Le moteur de ML sera ici.")

def page_bande_annonce():
    st.title("Bandes-annonces 🎥")
    with st.bar:
        selected = option_menu(
            menu_title="Entrer le titre du film dont vous voulez voir le trailer",        # Titre du menu (None pour cacher)
            options=["Accueil", "Upload", "Tâches"], # Les onglets
            icons=["house", "cloud-upload", "list-task"], # Icônes Bootstrap
            menu_icon="cast",                   # Icône du titre du menu
            default_index=0,                    # Quel onglet est ouvert par défaut
            orientation="horizontal",             # "vertical" ou "horizontal"
            # styles={...}                      # Dictionnaire CSS pour personnaliser les couleurs
        )
    st.write("Vidéos YouTube ici.")

def page_genre():
    st.title("Recherche par genre 🔍")
    st.write("Filtres par genre ici.")

def page_acteurs():
    st.title("Acteurs & Actrices ⭐️")
    st.write("Biographies ici (si données disponibles).")

# --- Barre latérale (Sidebar) & Navigation ---
with st.sidebar:
    st.header("Navigation")
    # On utilise un radio button ou un selectbox pour le menu
    # Proposition pour le menu: un radio button ou un selectbox  
    choix_page = st.radio(
        "Aller vers :",
        ["Accueil", "Recommandation", "Bande-annonce", "Recherche par Genre", "Acteurs"]
    )
    st.markdown("---")
    st.write("Projet Machine Learning")

# --- Gestion de l'affichage ---
if choix_page == "Accueil":
    page_accueil()
elif choix_page == "Recommandation":
    page_recommandation()
elif choix_page == "Bande-annonce":
    page_bande_annonce()
elif choix_page == "Recherche par Genre":
    page_genre()
elif choix_page == "Acteurs":
    page_acteurs()