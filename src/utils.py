import streamlit as st
import pandas as pd
import numpy as np
import sentry_sdk
import string
import math
from datetime import date
from typing import Any, List, Tuple

# Configuration de Sentry pour la gestion des erreurs
def setup_sentry():
    #st.page_link("pages/Compare.py", label="Compare", icon="1️⃣")
    sentry_sdk.init(
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        dsn = st.secrets["dns"],
        send_default_pii = True,
    )

## DATASET CLEANING FUNCTIONS ##

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

def clean_runtime(df):
    df['Runtime']=df['Runtime'].str.split(' ').str[0]
    df = df[df['Runtime'].notna() & ~df['Runtime'].str.contains('s', case=False, na=True)] #remove the runtime in seconde
    df['Runtime'] = df['Runtime'].apply(lambda x: int(x) if x not in ['', 'N/A'] else None)
    df = df.dropna(subset=['Runtime'])
    df['Runtime'] = df['Runtime'].astype(int)
    return df

def clean_reviews(df):
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
    
    return df['Review'].apply(clean_text)

def clean_votes(df):
    """Nettoie la colonne 'imdbVotes' d'un DataFrame et la convertit en float."""
    votes = df.copy()
    votes['imdbVotes'] = votes['imdbVotes'].replace(["N/A", ""], np.nan)
    votes = votes.dropna(subset=['imdbVotes'])
    votes['imdbVotes'] = votes['imdbVotes'].astype(str).str.replace(',', '')
    votes['imdbVotes'] = votes['imdbVotes'].apply(lambda x: float(x) if x not in ['', 'N/A', None] else np.nan)
    votes = votes.dropna(subset=['imdbVotes'])
    return votes

def clean_small_films(df):
    if df is None or df.empty:
        return pd.DataFrame()
    clean_df = clean_votes(df)
    clean_df = clean_runtime(clean_df)
    clean_df = clean_df[pd.to_numeric(clean_df['Runtime'], errors='coerce') >= 5]
    mask = ~((pd.to_numeric(clean_df['Runtime'], errors='coerce') < 20) & (clean_df['imdbVotes'] < 1000))
    clean_df = clean_df[mask]
    return clean_df

##

## DATASET EXTRACTION FUNCTIONS ##

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

def compute_quantiles(df):
    if df is None or df.empty:
        return 0, 0, 0, 0
    clean_df = clean_votes(df)
    clean_df = clean_df.sort_values(by=['imdbVotes'])
    q1 = np.quantile(clean_df['imdbVotes'], 0.05)
    q2 = np.quantile(clean_df['imdbVotes'], 0.20)
    q3 = np.quantile(clean_df['imdbVotes'], 0.50)
    return q1, q2, q3

def compute_categories(ref, df):
    q1, q2, q3 = compute_quantiles(ref)
    clean_df = clean_votes(df)

    intervals = [
        (clean_df['imdbVotes'] <= q1),             
        (clean_df['imdbVotes'] > q1) & (clean_df['imdbVotes'] <= q2),  
        (clean_df['imdbVotes'] > q2) & (clean_df['imdbVotes'] <= q3),  
        (clean_df['imdbVotes'] > q3)               
    ]

    counts = [len(clean_df[intervals[i]]) for i in range(4)]
    result = pd.DataFrame({
        'category': ['Obscure', 'Lesser-known', 'Well-known', 'Mainstream'],
        'number': counts
    })
    return result

##

def bind_categories(ref):
    q1, q2, q3 = compute_quantiles(ref)
    clean_ref = clean_votes(ref)
    clean_ref['category'] = clean_ref['imdbVotes'].apply(
        lambda x: 'Obscure' if x <= q1 else
                  'Lesser-known' if q1 < x <= q2 else
                  'Well-known' if q2 < x <= q3 else
                  'Mainstream'
    )
    return clean_ref

def make_movies_text(movie_list):
    movies = movie_list[:10]
    movies_text = "\n".join(f"• {m}<br>" for m in movies)
    if len(movie_list) > 10:
        movies_text += f"\n...and {len(movie_list) - 10} more"
    return movies_text

def make_movies_text_split(movie_list):
    movie_list=movie_list.split(', ')
    movies = movie_list[:10]
    movies_text = "\n".join(f"• {m}<br>" for m in movies)
    if len(movie_list) > 10:
        movies_text += f"\n...and {len(movie_list) - 10} more"
    return movies_text

def erreur_api():
      st.warning('The OMDB API is not working properly, try again later...', icon="⚠️")

def get_year_bounds(year):
    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)
    return first_day, last_day

def get_date_coordinates(data: pd.DataFrame, x: str) -> Tuple[Any, List[float], List[int]]:
    month_days = []
    for m in data[x].dt.month.unique():
        month_days.append(data.loc[data[x].dt.month == m, x].max().day)

    month_positions = np.linspace(1.5, 50, 12)
    weekdays_in_year = [i.weekday() for i in data[x]]

    # sometimes the last week of the current year conflicts with next year's january
    # pandas uses ISO weeks, which will give those weeks the number 52 or 53, but this
    # is bad news for this plot therefore we need a correction to use Gregorian weeks,
    # for a more in-depth explanation check
    # https://stackoverflow.com/questions/44372048/python-pandas-timestamp-week-returns-52-for-first-day-of-year
    weeknumber_of_dates = data[x].dt.strftime("%W").astype(int).tolist()

    return month_positions, weekdays_in_year, weeknumber_of_dates

