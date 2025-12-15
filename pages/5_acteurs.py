import pandas as pd
import streamlit as st
import numpy as np 
from utils import load_css

# --- Configuration des données ---

df = pd.read_csv('data\intervenants_merge_total.csv')
df_filtre = df[df['Biographie'] != 'Inconnu'].copy() # Utilisation de .copy() pour éviter SettingWithCopyWarning
df_filtre = df_filtre[['Identité', 'Photo de profil', 'Biographie']]
df_filtre.rename(columns={'Photo de profil': 'photo'}, inplace=True)
df_filtre['photo'] = "https://image.tmdb.org/t/p/w500" + df_filtre['photo']


# --- Configuration de la Page ---
st.set_page_config(
    page_title="SENECHAL MOVIE - Acteurs",
    layout="wide"
)
# --- Charger le style de la page ---
load_css()

# --- 1. Injection de CSS/Style (Pour le fond sombre et les couleurs) ---

# Ce bloc injecte du CSS dans la page pour changer l'apparence globale.
# Le fond de la maquette est sombre, avec du texte clair.
st.markdown("""
    <style>
    /* 1. Changer la couleur de fond du corps (background) en noir */
    .stApp {
        background-color: #1e1e1e; /* Gris très sombre / noir */
        color: white; /* Couleur du texte par défaut */
    }
    /* 2. Style pour les titres (header) */
    h1, h2, h3 {
        color: #FFFFFF; /* Blanc */
    }
    /* 3. Style pour les sous-titres/texte standard */
    p, label, .stMarkdown {
        color: #e0e0e0; /* Gris clair */
    }
    /* 4. Personnalisation du selectbox pour le rendre plus sombre */
    .stSelectbox label {
        color: white;
    }
    /* 5. Simuler le style de la police SENECHAL MOVIE (Police classique avec empattement) */
    h1, h2 {
        font-family: 'Times New Roman', serif; /* Simuler une police serif élégante */
        font-weight: 700;
        letter-spacing: 2px;
    }
    </style>
""", unsafe_allow_html=True)


#2. Contenu de la Page Acteurs/Actrices


st.title("🌟 SENECHAL MOVIE : Acteurs et Actrices")
st.subheader("Découvrez la biographie de vos stars préférées!")
st.markdown("---")

# --- Étape 1 : Sélection de l'Acteur ---

noms_acteurs = df_filtre['Identité'].tolist()

# Utiliser un conteneur pour centrer ou styliser le selectbox si besoin
col_gauche, col_milieu, col_droite = st.columns([1, 4, 1])

with col_milieu:
    acteur_selectionne = st.selectbox(
        'Veuillez sélectionner un acteur ou une actrice:',
        noms_acteurs,
        index=0
    )

# Récupérer les informations de l'acteur sélectionné
acteur_info = df_filtre[df_filtre['Identité'] == acteur_selectionne].iloc[0]

# --- Étape 2 : Affichage de la Biographie avec colonnes ---

# Utilisation de colonnes avec un peu plus de marge pour le corps principal
st.markdown("<br>", unsafe_allow_html=True) 
col_marge1, col_photo, col_bio, col_marge2 = st.columns([0.5, 1.5, 4, 0.5]) 

with col_photo:
    # Utilise un titre de couleur rouge pour rappeler le style CINEMA
    st.markdown(f"**<h2 style='color: #ff3333;'>{acteur_info['Identité']}</h2>**", unsafe_allow_html=True)
    
    # Cadre autour de l'image pour simuler le style "photo d'identité" ou "cadre" de la maquette
    st.image(
        acteur_info['photo'], 
        caption=f"Photo de {acteur_info['Identité']}", 
        use_container_width=True
    )
    
    # Ajout du style "Biographie" en bas
    st.markdown("<h3 style='color: white; border-bottom: 2px solid #ff3333;'>Biographie</h3>", unsafe_allow_html=True)
    

with col_bio:
    # Simuler le style de l'étoile de la célébrité au centre
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <h1 style='color: gold; font-size: 80px;'>★</h1>
            <h3 style='color: #ff3333;'>L'Étoile de la Célébrité</h3>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Affichage de la biographie
    st.markdown("<hr style='border: 1px solid #ff3333;'>", unsafe_allow_html=True)
    
    # Texte de la biographie (laisser en st.write pour un meilleur contrôle de la mise en page de Streamlit)
    st.write(acteur_info['Biographie'])
    
    st.markdown("<hr style='border: 1px solid #ff3333;'>", unsafe_allow_html=True)