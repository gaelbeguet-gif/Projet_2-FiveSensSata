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
