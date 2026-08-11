# modules externes
from google.oauth2 import service_account
import streamlit as st
import pandas as pd
import requests
import gspread
import json
import logging

# modules internes
from src.db.queries.qr_errors import add_movies_to_count
from src.db.queries.qr_profiles import *
from src.radar_graph import *
from src.utils import *
from src.db.queries.qr_movie import *

class ApiHandler:
    """ Classe pour gérer les interactions avec l'API Google Sheets
    et les feuilles de calcul associées"""

    def __init__(self):
        self.setup_omdb_api()
        # setup_sentry()

    ### PARTIE GSPREAD ###

    def add_profiles_to_db(self, profile, radar_stats):
        """ Ajoute ou met à jour les scores d'un profil dans la base de données"""
        add_profile_to_stats(profile, radar_stats)
    def add_profiles_to_stats_sheet(self, profile, radar_stats):
        """ Ajoute ou met à jour les scores d'un profil dans la feuille de calcul des statistiques des profils"""
        profile_id = profile['Username']
        existing_profiles = self.profiles_sheet.get_all_records()
        id_to_index = {row['id']: i for i, row in enumerate(existing_profiles) if 'id' in row}

        # Prépare la ligne à écrire
        row_data = [
            profile_id,
            radar_stats['Consommateur'],
            radar_stats['Explorateur'],
            radar_stats['Consensuel'],
            radar_stats['Éclectique'],
            radar_stats['Actif'],
            radar_stats['nb_films_vus'],
            str(radar_stats['ratio_peu_vus']).replace(',', '.'),
            str(radar_stats['moyenne_diff_rating']).replace(',', '.'),
            radar_stats['ratio_par_genre'],  # doit être une chaîne (JSON)
            radar_stats['nb_interactions'],
            1
        ]

        if profile_id in id_to_index:  # Si le profil existe, met à jour la ligne
            row_index = id_to_index[profile_id] + 2  # +2 pour header et indexation 1-based
            # Récupère la valeur actuelle de row[11] (compteur)
            current_row = self.profiles_sheet.row_values(row_index)
            current_count = int(current_row[11])
            row_data[11] = current_count + 1
            # Met à jour la ligne existante
            self.profiles_sheet.update(f'A{row_index}:L{row_index}', [row_data])
        else:  # Sinon, ajoute une nouvelle ligne
            self.profiles_sheet.append_row(row_data)

    def add_error_to_sheet(self, df_errors):
        """Ajoute les erreurs à la feuille de calcul des erreurs"""
        add_movies_to_count(df_errors)
        if(st.secrets['prod']==True):
            cleaned_rows = df_errors.map(sanitize).values.tolist()
            #self.error_sheet.append_rows(cleaned_rows)


    def get_all_mean(self):
        return get_global_stats()
    
    def get_all_means(self) :
        # Récupère les données de la feuille "profiles_stats" au format DataFrame pandas
        extraction = self.get_all_mean()

        res = {}
        res["Consommateur"] = round(extraction["nb_films_vus"])
        res["Explorateur"] = round(extraction["ratio_peu_vus"], 2)*100
        res["Consensuel"] = round(extraction["moyenne_diff_rating"], 3)

        # Pour la colonne "ratio_par_genre", on récupère le JSON de la première ligne
        ratio_dict = extraction["ratio_par_genre"]
        # Extraire uniquement le nom du premier genre (première clé) apparaissant dans le JSON
        res["Éclectique"] = next(iter(ratio_dict.keys()))

        res["Actif"] = round(extraction["nb_interactions"])

        return res

    ### PARTIE OMDB API ###

    def setup_omdb_api(self):
        """ Configure l'API OMDB avec la clé API"""
        self.base_url = 'http://www.omdbapi.com/'
        self.api_key_array = st.secrets['API_KEY_ARRAY']
        self.api_key_index = 0

    def switch_api_key(self):
        """ Change la clé API utilisée pour les requêtes OMDB"""
        self.api_key_index += 1
        if self.api_key_index >= len(self.api_key_array):
            logging.basicConfig(level=logging.INFO)
            logging.info("no more API keys")
            raise Exception("All API keys have been used up.")

    def get_movie_data_by_title(self, title, year):
        """ Récupère les données d'un film par son titre et son année via l'API OMDB.
        Elle est utilisée quand le film n'est pas dans la feuille de calcul. Peut changer la clé API si la limite de requêtes est atteinte."""
        year = np.int64(year)
        requestReponse = requests.get(self.base_url, params={'apikey': self.api_key_array[self.api_key_index], 't': title, 'y': year})
        response = requestReponse.json()
        status_code = requestReponse.status_code
        if response.get('Error') is not None:
            # sentry_sdk.capture_message(f"Movie not found: {row.to_dict()}")
            # print(response.get('Error'))
            if response['Error'] == "Request limit reached!":
                self.switch_api_key()
                response,status_code = self.get_movie_data_by_title(title, year)
        return response,status_code

    def get_movie_not_dl(self):
        return pd.read_csv("static/movie_not_dl.csv")

    def get_movie_db(self, df):
        return get_all_movies(df)
    
    def clean_response(self,value):
        """ Convertit les valeurs du CSV en booléens Python. """
        if pd.isna(value):
            return None
        if isinstance(value, bool):
            return value
        value = str(value).strip().upper()
        if value == "TRUE":
            return True
        if value == "FALSE":
            return False
        return None
    
    def insert_movies_to_db(self, df):
        df["imdbVotes"] = (
        df["imdbVotes"]
        .astype("string")
        .str.replace(",", "", regex=False)
        )

        df["imdbVotes"] = pd.to_numeric(
            df["imdbVotes"],
            errors="coerce"
        ).astype("Int64")

        df["Response"] = df["Response"].apply(self.clean_response)

        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )
        df = df.dropna(subset=["year"])
        df["Metascore"] = pd.to_numeric(
            df["Metascore"],
            errors="coerce"
        )

        df["imdbRating"] = pd.to_numeric(
            df["imdbRating"],
            errors="coerce"
        )

        return save_movies(df)
    
    def get_quantile(self):
        return compute_quantiles()

    def get_all_user_stats(self):
        return get_user_stats()