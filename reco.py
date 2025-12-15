# reco.py
import pandas as pd
import joblib
import unicodedata
from difflib import get_close_matches

# Chargement des données une seule fois à l'import du module
films = pd.read_csv("data/films.csv")
indices = joblib.load("data/indices_knn.joblib")

def normaliser_texte(texte: str) -> str:
    """Met le texte en minuscules, enlève les espaces inutiles et les accents."""
    texte = texte.lower().strip()
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("utf-8")
    return texte

# Colonne normalisée pour faciliter la recherche approximative
films["Titre_normalise"] = films["Titre"].apply(normaliser_texte)

def suggerer_titres(titre_saisi: str, n_suggestions: int = 5) -> list:
    """Propose des titres proches de ce que l'utilisateur a tapé."""
    titre_norm = normaliser_texte(titre_saisi)
    tous_les_titres_norm = films["Titre_normalise"].tolist()

    titres_proches_norm = get_close_matches(
        titre_norm,
        tous_les_titres_norm,
        n=n_suggestions,
        cutoff=0.5  # à ajuster si besoin
    )

    suggestions = []
    for titre_norm_proche in titres_proches_norm:
        titres_reels = films[films["Titre_normalise"] == titre_norm_proche]["Titre"].unique()
        suggestions.extend(list(titres_reels))

    suggestions_uniques = []
    for t in suggestions:
        if t not in suggestions_uniques:
            suggestions_uniques.append(t)

    return suggestions_uniques

def recommandation_films(titre: str, n_reco: int = 5) -> pd.DataFrame:
    """
    Retourne un DataFrame de films recommandés.
    Les lignes viennent de `films` aux indices retournés par le KNN.
    """
    info_film = films[films["Titre"] == titre]

    if info_film.empty:
        return films.iloc[0:0].copy()

    indice_film = info_film.index[0]

    reco_indices = indices[indice_film, 1:n_reco+1]
    df_reco = films.iloc[reco_indices, :].copy()

    return df_reco

#___________________________________________________________________________________#
def recommander_par_genre(genre: str, n_reco: int = 20) -> pd.DataFrame:
    """
    Retourne des films qui appartiennent au genre demandé.
    On peut trier par popularité, note, etc.
    """
    # Supposons que tu as une colonne "Genres" avec "Action|Comédie|..."
    df_filtre = films[films["Genres"].str.contains(genre, na=False)]

    # éventuellement trier :
    if "vote_average" in df_filtre.columns:
        df_filtre = df_filtre.sort_values("vote_average", ascending=False)

    return df_filtre.head(n_reco)

#___________________________________________________________________________________#

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def recommander_par_genres(genres_choisis: list, n_reco: int = 20) -> pd.DataFrame:
    # 1. récupérer les colonnes qui codent les genres
    genre_cols = [col for col in films.columns if col.startswith("genre_")]

    # 2. construire le vecteur utilisateur
    user_vec = np.zeros(len(genre_cols))
    for i, col in enumerate(genre_cols):
        genre_nom = col.replace("genre_", "")
        if genre_nom in genres_choisis:
            user_vec[i] = 1

    # 3. extraire la matrice des genres pour les films
    film_genres = films[genre_cols].values

    # 4. calculer la similarité cosinus
    sims = cosine_similarity(user_vec.reshape(1, -1), film_genres)[0]

    # 5. récupérer les indices des meilleurs films
    best_idx = sims.argsort()[::-1][:n_reco]

    df_result = films.iloc[best_idx].copy()
    df_result["score_genres"] = sims[best_idx]

    return df_result
