import streamlit as st
import pandas as pd

# --- GESTION DES IMPORTS ET DONNÉES DE SECOURS ---
try:
    from reco import suggerer_titres, recommandation_films
except ImportError:
    # Fallback enrichi pour que les détails (Budget, Trailer) fonctionnent sans le backend
    def suggerer_titres(t): return ["Titanic", "Avatar", "Inception"] if t else []
    def recommandation_films(t, n_reco=5): 
        return pd.DataFrame({
            "Titre": [f"Film Similaire {i}" for i in range(1, 6)],
            "Affiche du Film": ["https://via.placeholder.com/300x450?text=Affiche"] * 5,
            "Budget": ["100M$", "250M$", "50M$", "15M$", "200M$"],
            "Overview": ["Ceci est un résumé fictif pour tester l'affichage des détails du film."]*5,
            "Trailer": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]*5 # Rick Roll par défaut ;)
        })

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
            #4b0082 0%, #800080 10%, /* Rideau Gauche */
            #000000 20%, #000000 80%, /* Scène centrale noire */
            #800080 90%, #4b0082 100% /* Rideau Droit */
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
        background-color: #dda0dd; /* Couleur prune/rose */
        border-radius: 20px;
        padding: 15px 40px;
        box-shadow: 0px 0px 20px rgba(221, 160, 221, 0.6);
        text-align: center;
        color: #2c003e !important; /* Force la couleur foncée sur le rose */
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


# --- LOGIQUE DE NAVIGATION (SESSION STATE) ---
if 'page_actuelle' not in st.session_state:
    st.session_state['page_actuelle'] = 'recherche'

def aller_au_trailer(url):
    st.session_state['trailer_url'] = url
    st.session_state['page_actuelle'] = 'trailer'

def retour_recherche():
    st.session_state['page_actuelle'] = 'recherche'


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


    # 2. Zone de recherche
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        titre_saisi = st.text_input("Quel film avez-vous aimé ?", placeholder="Ex: Inception, Titanic...")
        
        if st.button("🔎 Chercher le film"):
            if not titre_saisi:
                st.warning("Merci de saisir un titre de film.")
            else:
                suggestions = suggerer_titres(titre_saisi)
                if not suggestions:
                    st.info("Aucun film ne correspond à cette saisie.")
                else:
                    st.session_state["suggestions"] = suggestions
                    # Reset
                    st.session_state.pop("titre_choisi", None)
                    st.session_state.pop("film_selectionne", None)

    # 3. Zone de sélection
    if "suggestions" in st.session_state:
        st.markdown("---")
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            titre_choisi = st.selectbox(
                "Confirmez votre film de départ :",
                st.session_state["suggestions"]
            )

            if st.button("✨ Lancer les recommandations ✨"):
                st.session_state["run_reco"] = True
                st.session_state["selected_movie_title"] = titre_choisi
                # On nettoie la sélection précédente
                st.session_state.pop("film_selectionne", None)

        # 4. Affichage des résultats
        if st.session_state.get("run_reco"):
            film_source = st.session_state["selected_movie_title"]
            
            # On stocke le dataframe dans la session pour ne pas le recharger à chaque clic
            if "df_reco" not in st.session_state or st.session_state.get("last_source") != film_source:
                st.session_state["df_reco"] = recommandation_films(film_source, n_reco=5)
                st.session_state["last_source"] = film_source
            
            df_reco = st.session_state["df_reco"]

            st.markdown(f"<h3 style='text-align: center; color: #dda0dd;'>Films recommandés si vous avez aimé : <i>{film_source}</i></h3>", unsafe_allow_html=True)
            st.write("") 

            if df_reco.empty:
                st.info("Pas de recommandations trouvées")
            else:
                n_cols = min(len(df_reco), 5)
                cols = st.columns(n_cols)

                # Boucle d'affichage
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
                        st.markdown(f"<div style='text-align:center; font-weight:bold; color: #e0e0e0; margin-top: 5px; height: 50px;'>{film['Titre']}</div>", unsafe_allow_html=True)
                        
                        # BOUTON "VOIR DETAILS"
                        if st.button("Voir la fiche", key=f"btn_{film['Titre']}"):
                            st.session_state["film_selectionne"] = film


    # 5. Zone de DÉTAILS (Apparaît au clic)
    if "film_selectionne" in st.session_state:
        sel_film = st.session_state["film_selectionne"]
        
        st.markdown("---")
        st.markdown(f"<h2 style='text-align:center; color:#dda0dd !important;'>Détails : {sel_film['Titre']}</h2>", unsafe_allow_html=True)
        
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
            st.markdown(f"**📝 Résumé :**")
            st.write(resume)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Bouton Trailer
            if st.button("🎥 Voir la Bande Annonce (Interne)"):
                aller_au_trailer(trailer)
        
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# VUE 2 : LECTEUR VIDEO (TRAILER)
# =========================================================
elif st.session_state['page_actuelle'] == '3_video.py':
    
    # Bouton retour
    if st.button("⬅️ Retour aux recommandations"):
        retour_recherche()
        st.rerun()

    st.markdown('<div class="pink-title-box" style="margin-top:20px;">🎥 SALLE DE PROJECTION</div>', unsafe_allow_html=True)
    
    col_v_1, col_v_2, col_v_3 = st.columns([1, 4, 1])
    with col_v_2:
        url = st.session_state.get('trailer_url', '')
        if url:
            st.video(url)
        else:
            st.warning("Désolé, lien vidéo introuvable.")

# --- PIED DE PAGE (Les Sièges) ---
st.markdown('<div class="seats-footer"></div>', unsafe_allow_html=True)