# modules externes
import streamlit as st
import requests
import logging

# modules internes
from src.db.queries.qr_user import *
from src.services.radar_graph import *
from src.utils.utils import *
from src.db.queries.qr_movie import *

class ApiHandler:
    """ Classe pour gérer les interactions avec l'API OMDB"""

    def __init__(self):
        self.setup_omdb_api()

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
    