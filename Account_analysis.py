import streamlit as st
from src.solo import *
import zipfile
import tempfile
import gspread
from google.oauth2 import service_account
import sentry_sdk
import math
import json

st.set_page_config(
    page_title="Letterboxd analysis",
    page_icon="🎥",
    layout="wide",
    menu_items={
        'Report a bug': "mailto:lelan.quentin56@gmail.com",
    }
)

st.markdown("""
# 🎬 Welcome to our **Letterboxd Profile Analyzer**!

With just a few clicks, you'll discover your movie habits and get interesting insights about your film preferences, all your letterboxd stat !.  

🚀 This is just the first version of the project — many improvements are planned, including a feature to compare two profiles!

---

## 📥 How to get started:

1. **Log into** your Letterboxd account (on pc)
2. Go to **Settings → Data → Export Your Data**
3. **Download** the data file
4. **Upload** the zipfile below and enjoy your personalized analysis!

---
""")
#st.page_link("pages/Compare.py", label="Compare", icon="1️⃣")
sentry_sdk.init(
    dsn= st.secrets["dns"],
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

with st.spinner("Set-up...", show_time=False):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open("all_movies_data")
    sheet = spreadsheet.sheet1

    # Charger les données existantes depuis Google Sheet
    data = sheet.get_all_records()

    error_sheet = spreadsheet.worksheet("error")
temp_dir = tempfile.TemporaryDirectory()
temp_name=temp_dir.name

base_url = 'http://www.omdbapi.com/'
api_key_array=st.secrets['API_KEY_ARRAY']

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 1

uploaded_files = st.file_uploader(
    "Choose your zip file", accept_multiple_files=False, key=st.session_state["uploader_key"]
)

def sanitize(value):
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ''
    return value

def getMovie(all_movies, dfF, sheet):
    df_errors = pd.DataFrame(columns=["filename", "error", *dfF.columns])
    progress_text = "Get movie data. Please wait. (It's a free project, so there might be data limitations or errors in the dataset.)"
    my_bar = st.progress(0, text=progress_text)
    df_movie = pd.DataFrame()

    existing_movies = set(
        zip(all_movies['Title'].dropna().astype(str), all_movies['Year'].dropna())
    )
    i = 0
    api_key=api_key_array[0]
    key_index=0
    # Itérer sur les lignes de dfF pour comparer (Name, Year)
    for _, row in dfF.iterrows():
        title_year = (row['Name'], row['Year'])
        if title_year not in existing_movies:
            try:
                movie_data = get_movie_data_by_title(row['Name'], row['Year'], base_url, api_key) 
                #print(movie_data)
                if movie_data.get('Error') is not None:
                    #sentry_sdk.capture_message(f"Movie not found: {row.to_dict()}")
                    #print(row)
                    df_errors.loc[len(df_errors)] = [uploaded_files.name, movie_data['Error'], *row.values]
                        #if too much movie we switch the api_key
                    if movie_data['Error']=="Request limit reached!":
                        key_index=key_index+1
                        if key_index < len(api_key_array):
                            print(key_index)
                            api_key=api_key_array[key_index]
                else:
                    df_movie = pd.concat([df_movie, pd.DataFrame([movie_data])], ignore_index=True)
            except Exception as e:
                #sentry_sdk.capture_message(f"Movie not found: {row.to_dict()}")
                #print(row)
                df_errors.loc[len(df_errors)] = [uploaded_files.name, str(e), *row.values]
        my_bar.progress(int(100 * i / len(dfF)), text=progress_text)
        i += 1

    if not df_errors.empty:
        cleaned_rows = df_errors.applymap(sanitize).values.tolist()
        error_sheet.append_rows(cleaned_rows)

    if len(df_movie) != 0:
        df_movie['Ratings'] = df_movie['Ratings'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
        df_movie = clean_year(df_movie)

        rows = df_movie.applymap(sanitize).values.tolist()
        sheet.append_rows(rows)

        all_movies = pd.concat([all_movies, df_movie]).drop_duplicates(subset=['Title', 'Year'])

        # peut ajouter chaque nouvelle ligne, plutot que tout effacer
        #sheet.clear()  # Efface l'ancienne feuille
        #sheet.update([all_movies.columns.values.tolist()] + all_movies.values.tolist())

    my_bar.empty()
    return all_movies

def general_info():
    runtime=computeRuntime(watch_df)
    runtimeW =computeRuntime(watchlist_df)
    st.title('Global info')
    col,col2,col3 = st.columns(3)
    with col:
        st.markdown(f"<h1><span style='color:#83c9ff'>{round(runtime)}</span> hours watched</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1><span style='color:#83c9ff'>{len(watch_df.index)}</span> movies watched</h1>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<h1><span style='color:#83c9ff'>{len(watch_df['Director'].unique())}</span> directors</h1>", unsafe_allow_html=True)
    col4,col5 = st.columns(2)
    with col4:
        st.markdown(f"<h1><span style='color:#83c9ff'>{round(runtimeW)}</span> hours to watch</h1>", unsafe_allow_html=True)
    with col5:
        st.markdown(f"<h1><span style='color:#83c9ff'>{len(watchlist_df.index)}</span> movies to watch</h1>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    div[data-testid="stTabs"]{
        padding-top:30px;
    }
    /* Sélectionner les titres des tabs */
    div[data-baseweb="tab-list"] > button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] {
        font-size: 30px; /* Changer la taille ici */
        min-width:200px;
    }

    @media(max-width:610px) {
        div[data-baseweb="tab-list"] > button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] {
        font-size: inherit; /* Changer la taille ici */
        min-width:inherit;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
if uploaded_files is not None:
    try:
        with zipfile.ZipFile(uploaded_files, 'r') as zip_ref:
            zip_ref.extractall(temp_name)
        
        watchlist=pd.read_csv(temp_name+'/watchlist.csv')
        watched=pd.read_csv(temp_name+'/watched.csv')
        rating=pd.read_csv(temp_name+'/ratings.csv')
        reviews=pd.read_csv(temp_name+'/reviews.csv')

        watchlist = clean_year(watchlist)
        watched=clean_year(watched)
        rating=clean_year(rating)
        corpus=clean_reviews(reviews)

        #all_movies=pd.read_csv('./data/all_movies_data.csv')
        all_movies = pd.DataFrame(data)
        all_movies=clean_year(all_movies)
        dfF=pd.concat([watched,watchlist])

        all_movies = getMovie(all_movies, dfF, sheet)

        watch_df = pd.merge(watched, all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()
        watchlist_df=pd.merge(watchlist, all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()

        rating_df=pd.merge(rating, all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()
        rating_df['Rating']=rating_df['Rating']*2
        rating_df=clean_imdbr(rating_df)
        rating_df['diff_rating']=rating_df['Rating']-rating_df['imdbRating']

        q1,q2,q3=compute_quartile(all_movies)

        ### DEBUT INTERFACE
        general_info()
        #movie_per_year(watch_df)

        tab1, tab2, tab3 = st.tabs(["Watched", "Watchlist","Rating"])
        #WATCHED
        with tab1:
            st.header("Some stats on the movies you've seen", divider='blue')
            genre(watch_df)
            watched_actor_col, watched_director_col = st.columns(2)
            bottom,top=famous(watch_df)
            with watched_actor_col:
                fig=actor(watch_df)
                st.plotly_chart(fig)
            with watched_director_col:
                fig=director(watch_df)
                st.plotly_chart(fig)
            st.header("Lesser-known and better-known films by number of IMDB votes", divider='blue')
            most_watched_col, less_watched_col = st.columns(2)
            with less_watched_col:
                st.write("Lesser-known movie watched")
                st.write(bottom)
            with most_watched_col:
                st.write("Better-known movie watched")
                st.write(top)
            cinephile(watch_df,q1,q2,q3,"a")
            decade(watch_df)
            runtime_bar(watch_df)
            mapW(watch_df)
        #WATCHLIST
        with tab2:
            st.header("Some stats on the films you want to see", divider='blue')
            genre(watchlist_df)
            watched_actor_col, watched_director_col = st.columns(2)
            bottom,top=famous(watchlist_df)
            with watched_actor_col:
                fig=actor(watchlist_df)
                st.plotly_chart(fig)
            with watched_director_col:
                fig=director(watchlist_df)
                st.plotly_chart(fig)
            st.header("Lesser-known and better-known films by number of IMDB votes", divider='blue')
            most_watched_col, less_watched_col = st.columns(2)
            with less_watched_col:
                st.write("Lesser-known movie in your watchlist")
                st.write(bottom)
            with most_watched_col:
                st.write("Better-known movie in your watchlist")
                st.write(top)
            cinephile(watchlist_df,q1,q2,q3,"b")
            decade(watchlist_df)
            runtime_bar(watchlist_df)
            mapW(watchlist_df)
        #RATING
        with tab3:
            st.header("Some stats on your ratings", divider='blue')
            sur_note,sous_note=diff_rating(rating_df)
            st.write('The movies you rated most compared to IMDB')
            st.write(sur_note)
            st.write('The movies you most underrated compared to IMDB')
            st.write(sous_note)
            rating_director(rating_df,watch_df)
            rating_actor(rating_df)
            genre_rating(rating_df)
            comparaison_rating(rating_df)
            if(len(corpus)!=0):
                st.header("A wordcloud with your reviews", divider='blue')
                generate_wordcloud(corpus)

    except zipfile.BadZipFile:
        st.session_state["uploader_key"] += 1
        #trick to remove bad file
        st.warning('This is not a zipfile', icon="⚠️")
        st.rerun()
    except FileNotFoundError:
        st.write(f"File not found.")
temp_dir.cleanup()


#st.sidebar.title("About")
st.info(
    """
    Follow me on Letteboxd : [exodus_](https://letterboxd.com/exodus_/)

    This app is maintained by [Exodus](https://exodusg.github.io/) and [Montro](https://github.com/Montr0-0).
    
    Report a bug : [send a email with your zipfile](mailto:lelan.quentin56@gmail.com) 
"""
)