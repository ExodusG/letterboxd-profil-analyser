import streamlit as st
import pandas as pd
import numpy as np
import sentry_sdk
import string
import math

# Configuration de Sentry pour la gestion des erreurs
def setup_sentry():
    #st.page_link("pages/Compare.py", label="Compare", icon="1️⃣")
    sentry_sdk.init(
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        dsn = st.secrets["dns"],
        send_default_pii = True,
    )

def sanitize(value):
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ''
    return value

def clean_year(df):
    df = df[pd.to_numeric(df['Year'], errors='coerce').notna()]
    df['Year'] = df['Year'].astype(float).astype(int).astype(str)
    return df

def clean_imdbv(df):
    df['imdbVotes'] = df['imdbVotes'].replace("N/A", np.nan)
    df = df.dropna(subset=['imdbVotes'])
    df['imdbVotes'] = df['imdbVotes'].str.replace(',', '').astype(float)
    return df

def clean_imdbr(df):
    df['imdbRating'] = df['imdbRating'].replace("N/A", np.nan)
    df = df.dropna(subset=['imdbRating'])
    df['imdbRating'] = df['imdbRating'].apply(lambda x: float(x) if x != '' else None)
    return df

def extract_year(df, year):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df_year = df[df['Date'].dt.year == year]
    return df_year

def computeRuntime(df):
    df['Runtime']=df['Runtime'].replace('nan', np.nan)
    df = df.dropna(subset=['Runtime'])
    df['Runtime'] = df['Runtime'].astype(str).str.replace(r'[Ss]', '5', regex=True)

    runtimeW=df['Runtime'].str.split(' ').str[0]
    runtimeW = runtimeW.apply(lambda x: int(x) if x not in ['', 'N/A'] else None)
    runtimeW=runtimeW.sum() / 60
    return runtimeW

def compute_quartile(df):
    quartile = df.copy()
    if df is None or df.empty:
        return 0, 0, 0
    else :
        quartile['imdbVotes'] = quartile['imdbVotes'].replace("N/A", np.nan)
        quartile = quartile.dropna(subset=['imdbVotes'])
        quartile['imdbVotes'] = quartile['imdbVotes'].astype(str).str.replace(',', '')
        quartile['imdbVotes'] = quartile['imdbVotes'].apply(
            lambda x: float(x) if x not in ['', 'N/A'] else np.nan
        )
        #quartile['imdbVotes'] = quartile['imdbVotes'].apply(lambda x: float(x) if x != '' else np.nan)
        quartile = quartile.dropna(subset=['imdbVotes'])
        quartile = quartile.sort_values(by=['imdbVotes'])

        q1 = np.quantile(quartile['imdbVotes'], 0.25)
        q2 = np.quantile(quartile['imdbVotes'], 0.50)
        q3 = np.quantile(quartile['imdbVotes'], 0.75)
    return q1, q2, q3


def clean_reviews(reviews_df):
    def clean_text(text):
        if not isinstance(text, str):
            return ''
        # Minuscule
        text = text.lower()
        # Remplacer apostrophes et retours à la ligne
        text = text.replace("'", " ").replace("\n", " ")
        # Supprimer ponctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Normaliser et supprimer accents
        #text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
        #supprime les mots en dessous de 3 char
        words = text.split()
        words = [word for word in words if len(word) >= 3]
        text = ' '.join(words)
        return text.strip()
    
    return reviews_df['Review'].apply(clean_text)

def compute_categories(ref, df):
    q1, q2, q3 = compute_quartile(ref)

    df['imdbVotes'] = df['imdbVotes'].replace("N/A", np.nan)
    df['imdbVotes'] = df['imdbVotes'].replace("", np.nan)
    df = df.dropna(subset=['imdbVotes'])
    df['imdbVotes'] = df['imdbVotes'].apply(
    lambda x: float(x.replace(',', '')) if isinstance(x, str) else x
    )

    # Définir les bornes des intervalles
    intervals = [
        (df['imdbVotes'] <= q1),             # Intervalle 0 <= Q1
        (df['imdbVotes'] > q1) & (df['imdbVotes'] <= q2),  # Intervalle Q1 < Q2
        (df['imdbVotes'] > q2) & (df['imdbVotes'] <= q3),  # Intervalle Q2 < Q3
        (df['imdbVotes'] > q3)               # Intervalle Q3 < inf
    ]

    # Créer un tableau avec les comptages pour chaque intervalle
    counts = [
        len(df[intervals[0]]), 
        len(df[intervals[1]]), 
        len(df[intervals[2]]), 
        len(df[intervals[3]])
    ]
    result = pd.DataFrame({
        'category': [' Obscure', 'Lesser-known', 'Well-known', 'Mainstream'],
        'number': counts
    })
    return result

def erreur_api():
      st.warning('The OMDB API has a problem, you can try later', icon="⚠️")