from src.utils import compute_categories
import numpy as np
import json


def compute_radar_stats_for_sheet(ref, watched_df, rating_df, reviews_df, comments_df, profiles_stats):
    scores = compute_scores(ref, watched_df, rating_df, reviews_df, comments_df, profiles_stats)
    markers = compute_markers(ref, watched_df, rating_df, reviews_df, comments_df)
    return {**scores, **markers}

### PARTIE SCORE ###

#   Consommateur   : Mesure le visionnage de films en général, sans distinction de popularité.
#   Explorateur    : Mesure le visionnage de films peu populaires (hypothèse : peu populaires = peu notés).
#   Consensuel     : Indique le niveau d'accord entre les préférences de l'utilisateur et celles de la communauté.
#   Éclectique     : Reflète la variété des préférences de l'utilisateur à travers différentes catégories.
#   Actif          : Représente le niveau d'activité et d'interaction de l'utilisateur sur la plateforme.

# Calcul des scores pour chaque composante
def compute_scores(ref, watched_df, rating_df, reviews_df, comments_df, profiles_stats):
    scores = {
        "Consommateur": 0,
        "Explorateur": 0,
        "Consensuel": 0,
        "Éclectique": 0,
        "Actif": 0
    }

    # Calcul des scores pour chaque composante
    scores["Consommateur"]  = compute_consommateur_score(watched_df, profiles_stats)
    scores["Explorateur"]   = compute_explorateur_score(ref, watched_df, profiles_stats)
    scores["Consensuel"]    = compute_consensuel_score(rating_df, profiles_stats)
    scores["Éclectique"]    = compute_eclectique_score(watched_df, profiles_stats)
    scores["Actif"]         = compute_actif_score(reviews_df, comments_df, profiles_stats)

    return scores

def compute_consommateur_score(watched_df, profiles_stats):
    marker = compute_consommateur_marker(watched_df)
    all_markers = np.array(profiles_stats['nb_films_vus'])
    consommateur = smart_percentile(marker, all_markers)
    return consommateur

def compute_explorateur_score(ref, watched_df, profiles_stats):
    marker = compute_explorateur_marker(ref, watched_df)
    all_markers = np.array(profiles_stats['ratio_peu_vus'])
    explorateur = smart_percentile(marker, all_markers)
    return explorateur

def compute_consensuel_score(rating_df, profiles_stats):
    marker = abs(compute_consensuel_marker(rating_df))
    all_markers = np.array(profiles_stats['moyenne_diff_rating'])
    all_markers = abs(all_markers)
    consensuel = smart_percentile(marker, all_markers)
    return consensuel

def compute_eclectique_score(watched_df, profiles_stats):
    ratio_par_genre = compute_eclectique_marker(watched_df)
    user_ratios = json.loads(ratio_par_genre)

    all_ratios = []
    for r in profiles_stats['ratio_par_genre']:
        d = json.loads(r)
        all_ratios.append(d)
    
    all_genres = set()
    for ratios in all_ratios:
        all_genres.update(ratios.keys())
    all_genres = sorted(all_genres)  # pour un ordre fixe

    ratio_matrix = np.array([
        [ratios.get(genre, 0.0) for genre in all_genres]
        for ratios in all_ratios
    ])

    genre_means = np.mean(ratio_matrix, axis=0)

    distances = np.sum(np.abs(ratio_matrix - genre_means), axis=1)

    user_vector = np.array([user_ratios.get(genre, 0.0) for genre in all_genres])
    user_distance = np.sum(np.abs(user_vector - genre_means))

    eclectique = smart_percentile(user_distance, distances)
    return eclectique

def compute_actif_score(reviews_df, comments_df, profiles_stats):
    marker = compute_actif_marker(reviews_df, comments_df)
    all_marker = np.array(profiles_stats['nb_interactions'])
    actif = smart_percentile(marker, all_marker)
    return actif

###

### PARTIE INDICATEURS ###

#   Consommateur   : nombre de films vus 
#   Explorateur    : rapport entre le nombre de films peu vus (Obscure + Lesser-known) et le nombre total de films vus
#   Consensuel     : moyenne des diffRating
#   Éclectique     : pour chaque genre, le nombre de films vus dans ce genre divisé par le nombre total de films vus
#   Actif          : nombre de commentaires laissés + nombre de reviews laissés

# Calcul des scores pour chaque composante
def compute_markers(ref, watched_df, rating_df, reviews_df, comments_df):
    markers = {
        "nb_films_vus": 0,
        "ratio_peu_vus": 0,
        "moyenne_diff_rating": 0,
        "ratio_par_genre": {},
        "nb_interactions": 0
    }

    # Calcul des scores pour chaque composante
    markers["nb_films_vus"]         = compute_consommateur_marker(watched_df)
    markers["ratio_peu_vus"]        = compute_explorateur_marker(ref, watched_df)
    markers["moyenne_diff_rating"]  = compute_consensuel_marker(rating_df)
    markers["ratio_par_genre"]      = compute_eclectique_marker(watched_df)
    markers["nb_interactions"]      = compute_actif_marker(reviews_df, comments_df)

    return markers

def compute_consommateur_marker(watched_df):
    marker = int(len(watched_df))
    return marker

def compute_explorateur_marker(ref, watched_df):
    marker = int(compute_categories(ref, watched_df)['number'][0] + compute_categories(ref, watched_df)['number'][1])
    marker = round(marker / len(watched_df), 3) if len(watched_df) > 0 else 0
    return marker

def compute_consensuel_marker(rating_df):
    marker = round(rating_df['diff_rating'].mean() if ('diff_rating' in rating_df.columns and len(rating_df['diff_rating']) > 0) else 0, 3)
    return marker

def compute_eclectique_marker(watched_df):
    genres_series = watched_df['Genre'].dropna().apply(lambda x: [g.strip() for g in x.split(',')])
    exploded_genres = genres_series.explode()
    genre_counts = exploded_genres.value_counts()
    total_films = len(watched_df)
    ratio_par_genre = round((genre_counts / total_films), 3).to_dict()
    ratio_par_genre = json.dumps(ratio_par_genre, ensure_ascii=False)
    return ratio_par_genre

def compute_actif_marker(reviews_df, comments_df):
    marker = len(reviews_df) + len(comments_df)
    return marker

### PARTIE INDICATEURS ###

def smart_percentile(marker, all_markers):
    all_markers = list(all_markers)
    if marker in all_markers:
        all_markers.remove(marker)
    if not all_markers:
        return 50
    count = np.sum(np.array(all_markers) <= marker)
    percentile = count / len(all_markers)
    score = int(round(percentile * 100))

    if score == 0:
        score = 1
    elif score == 100:
        score = 99

    return score