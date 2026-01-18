# modules externes
import re
from google.oauth2 import service_account
import sentry_sdk
import streamlit as st
import pandas as pd
import requests
import gspread
import json
import logging

# modules internes
from src.utils import sanitize, clean_year

class ApiHandler:
    """ Classe pour gérer les interactions avec l'API Google Sheets
    et les feuilles de calcul associées"""

    def __init__(self):
        self.setup_gspread_connection()
        self.get_worksheets()
        self.setup_omdb_api()
        self.setup_sentry()
        self.http_session = requests.Session()

    
    # Configuration de Sentry pour la gestion des erreurs
    def setup_sentry(self):
        #st.page_link("pages/Compare.py", label="Compare", icon="1️⃣")
        sentry_sdk.init(
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            dsn = st.secrets["dns"],
            send_default_pii = True,
        )

    ### PARTIE GSPREAD ###
    
    def setup_gspread_connection(self):
        """ Configure la connexion à Google Sheets avec les informations d'identification du service"""
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        self.gspread_client = gspread.authorize(credentials)
    
    def get_worksheets(self):
        """ Récupère les feuilles de calcul nécessaires et les stocke dans un dictionnaire."""
        spreadsheet = self.gspread_client.open(st.secrets["sheet_name"])
        self.worksheets = {
            "all_movies_data": spreadsheet.worksheet("all_movies_data"),
            "profiles_stats": spreadsheet.worksheet("profiles_stats"),
            "error": spreadsheet.worksheet("error"),
            "movie_not_dl": spreadsheet.worksheet("movie_not_dl")
        }
        self.films_sheet = self.worksheets["all_movies_data"]
        self.profiles_sheet = self.worksheets["profiles_stats"]
        self.error_sheet = self.worksheets["error"]
        self.film_not_dl = self.worksheets["movie_not_dl"]

    def get_data_from_sheet(self, sheet_name):
        """ Récupère les données d'une feuille de calcul en utilisant les références stockées."""
        if sheet_name not in self.worksheets:
            raise ValueError(f"La feuille de calcul '{sheet_name}' n'est pas initialisée.")
        sheet = self.worksheets[sheet_name]
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    
    def add_movies_to_sheet(self, df_movies):
        """ Ajoute les films à la feuille de calcul"""
        df_movies['Ratings'] = df_movies['Ratings'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
        df_movies = clean_year(df_movies)
        rows = df_movies.astype(object).apply(lambda col: col.map(sanitize)).values.tolist()
        # peut ajouter chaque nouvelle ligne, plutot que tout effacer
        #sheet.clear()  # Efface l'ancienne feuille
        #sheet.update([all_movies.columns.values.tolist()] + all_movies.values.tolist())
        self.films_sheet.append_rows(rows) 

    def add_profiles_to_stats_sheet(self, profile, radar_stats):
        """ Ajoute ou met à jour les scores d'un profil dans la feuille de calcul des statistiques des profils"""
        profile_id = profile['Username']
        ids = self.profiles_sheet.col_values(1)
        
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

        try:
            row_index = ids.index(profile_id) + 2  # +2 pour header et indexation 1-based
            current_count = int(self.profiles_sheet.cell(row_index, 12).value or 1) # row[11] (compteur)
            row_data[11] = current_count + 1
            self.profiles_sheet.update(f'A{row_index}:L{row_index}', [row_data])
        except ValueError:  # Sinon, ajoute une nouvelle ligne
            self.profiles_sheet.append_row(row_data)

    def add_error_to_sheet(self, df_errors):
        """Ajoute les erreurs à la feuille de calcul des erreurs"""
        if(st.secrets['prod']==True):
            cleaned_rows = df_errors.astype(object).apply(lambda col: col.map(sanitize)).values.tolist()
            self.error_sheet.append_rows(cleaned_rows)

    def get_all_means(self, df_profiles_stats=None):
        # Récupère les données de la feuille "profiles_stats" au format DataFrame pandas
        if df_profiles_stats is None:
            df_profiles_stats = self.get_data_from_sheet("profiles_stats")
        
        if df_profiles_stats.empty:
            return {
                "Consommateur": 0,
                "Explorateur": 0,
                "Consensuel": 0,
                "Éclectique": "",
                "Actif": 0
            }
    
        res = {
            "Consommateur": round(df_profiles_stats["nb_films_vus"].mean()),
            "Explorateur": round(df_profiles_stats["ratio_peu_vus"].mean(), 2)*100,
            "Consensuel": round(df_profiles_stats["moyenne_diff_rating"].mean(), 3),
            "Éclectique": "",
            "Actif": round(df_profiles_stats["nb_interactions"].mean())
        }

        # Pour la colonne "ratio_par_genre", on récupère le JSON de la première ligne
        ratio_str = df_profiles_stats["ratio_par_genre"].iloc[0]
        ratio_dict = json.loads(ratio_str)
        # Extraire uniquement le nom du premier genre (première clé) apparaissant dans le JSON
        res["Éclectique"] = next(iter(ratio_dict.keys()))
    
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
        params={'apikey': self.api_key_array[self.api_key_index], 't': title, 'y': year}
        requestReponse = self.http_session.get(self.base_url, params=params, timeout=10)
        response = requestReponse.json()
        status_code = requestReponse.status_code

        if response.get('Error') is not None:
            # sentry_sdk.capture_message(f"Movie not found: {row.to_dict()}")
            # print(response.get('Error'))
            if response['Error'] == "Request limit reached!":
                self.switch_api_key()
                response,status_code = self.get_movie_data_by_title(title, year)

        return response, status_code




