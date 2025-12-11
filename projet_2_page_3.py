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

# Chargement des données (avec cache pour la performance)
@st.cache_data
def charger_donnees():
    # Adapter le chemin si nécessaire
    df = pd.read_csv("films.csv")
    df['Lien_vidéo'] = df['Lien_vidéo'].fillna('')
    df['Affiche du Film'] = df['Affiche du Film'].fillna('')
    df['Résumé'] = df['Résumé'].fillna("Pas de résumé disponible.")
    return df

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
    df = charger_donnees()
    st.title("Bandes-annonces 🎥")

    # --- 1. Gestion de l'état (Session State) ---
    if 'film_actuel' not in st.session_state:
        st.session_state['film_actuel'] = None

    # Fonction pour mettre à jour le film (Callback)
    def changer_film(film_row):
        st.session_state['film_actuel'] = film_row

    # --- 2. Barre de recherche ---
    titres_disponibles = df['Titre'].unique()
    
    # On détecte le changement directement ici
    choix_titre = st.selectbox(
        "Rechercher un film :", 
        options=titres_disponibles,
        index=None,
        placeholder="Tapez le nom d'un film..."
    )

    # Si l'utilisateur utilise la barre de recherche, on met à jour
    if choix_titre:
        film_search = df[df['Titre'] == choix_titre].iloc[0]
        # On ne met à jour que si c'est différent pour ne pas bloquer les boutons
        if st.session_state['film_actuel'] is None or st.session_state['film_actuel']['Titre'] != film_search['Titre']:
            st.session_state['film_actuel'] = film_search

    # --- 3. Lecteur Vidéo ---
    film = st.session_state['film_actuel']

    if film is not None:
        st.divider()
        col_video, col_infos = st.columns([2, 1])
        
        with col_video:
            st.subheader(f"🎬 {film['Titre']}")
            lien = film['Lien_vidéo']
            if lien and "http" in str(lien):
                st.video(lien)
            else:
                st.warning("Bande-annonce non disponible.")

        with col_infos:
            st.subheader("Résumé")
            st.info(film['Résumé'])
    else:
        st.info("Sélectionnez un film ou cliquez sur une suggestion ci-dessous.")

    # --- 4. Suggestions cliquables ---
    st.divider()
    st.subheader("Suggestions")

    # Remplace par ton ML ici : suggestions = ton_ml_function()
    suggestions = df.sample(5)

    cols = st.columns(5)
    
    for col, (_, film_sugg) in zip(cols, suggestions.iterrows()):
        with col:
            # Affiche
            affiche = film_sugg['Affiche du Film']
            if affiche and "http" in str(affiche):
                st.image(affiche, use_container_width=True)
            else:
                st.write("🎞️")
            
            # LE FIX EST ICI : on utilise 'on_click'
            # Cela force la mise à jour de la variable AVANT de recharger la page
            st.button(
                f"Voir {film_sugg['Titre']}", 
                key=f"btn_{film_sugg['tconst']}", # Clé unique indispensable
                on_click=changer_film,     # La fonction à appeler
                args=(film_sugg,)          # L'argument à passer à la fonction
            )

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