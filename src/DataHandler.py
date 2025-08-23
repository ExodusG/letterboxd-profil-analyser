# modules externes
import zipfile
import pandas as pd
import tempfile
from datetime import datetime
import pycountry
from wordcloud import WordCloud
from stop_words import get_stop_words
import os

# modules internes
import src.ApiHandler as api_handler
import src.GraphMaker as graph_maker
from src.utils import *
from src.radar_graph import compute_radar_stats_for_sheet


class DataHandler:

    def __init__(self):
        self.api_handler    = api_handler.ApiHandler()
        self.graph_maker    = graph_maker.GraphMaker()
        self.temp_dir       = tempfile.TemporaryDirectory()
        self.temp_name      = self.temp_dir.name

### Initialisation des données

    def setup_worksheets_data(self):
        """ Configure les données des feuilles de calcul"""
        self.films_data = self.api_handler.get_data_from_sheet("all_movies_data")
        self.profiles_data = self.api_handler.get_data_from_sheet("profiles_stats")

    def get_films(self, all_movies, dfF, my_bar):
        """ Récupère les films manquants dans all_movies à partir de dfF"""
        
        df_errors   = []
        df_movies   = []
        total_movies = len(dfF)
        existing_movies = set(
            zip(all_movies['Title'].dropna().astype(str), all_movies['Year'].dropna())
        )

        for i, (_, row) in enumerate(dfF.iterrows()):
            title_year = (row['Name'], row['Year'])
            if title_year not in existing_movies:
                try:
                    films_data,status_code = self.api_handler.get_movie_data_by_title(row['Name'], row['Year'])
                    if status_code ==503:
                        return None
                    if films_data.get('Error') is not None:
                        df_errors.append([self.uploaded_files.name, films_data['Error'], *row.values])
                    else:
                        df_movies.append(films_data)
                except Exception as e:
                    # sentry_sdk.capture_message(f"Movie not found: {row.to_dict()}")
                    df_errors.append([self.uploaded_files.name, str(e), *row.values])
            my_bar.progress(
                int(100 * (i+1) / total_movies),
                text="Getting movie data, Please wait. (It's a free project, so there might be data limitations or errors in the dataset)"
            )

        if df_errors:
            df_errors_df = pd.DataFrame(df_errors, columns=['File', 'Error', *dfF.columns])
            self.api_handler.add_error_to_sheet(df_errors_df)

        if df_movies:
            df_movies_df = pd.DataFrame(df_movies)
            self.api_handler.add_movies_to_sheet(df_movies_df)
            self.all_movies = pd.concat([all_movies, df_movies_df]).drop_duplicates(subset=['Title', 'Year'])

        my_bar.empty()
        return all_movies
    
    def setup_user_upload(self, uploaded_files, my_bar,exemple):
        """ Configure les données de l'utilisateur à partir du fichier zip téléchargé"""
        if uploaded_files is not None:
            try:
                if exemple is None:
                    self.uploaded_files = uploaded_files
                    tmp_name=self.temp_name
                    with zipfile.ZipFile(uploaded_files, 'r') as zip_ref:
                        zip_ref.extractall(tmp_name)
                else:
                    tmp_name=exemple
                # Lecture des fichiers CSV attendus
                csv_files = ['watchlist', 'watched', 'ratings', 'reviews', 'profile', 'comments']
                dataframes = {}
                for csv_name in csv_files:
                    file_path = os.path.join(tmp_name, f'{csv_name}.csv')
                    dataframes[csv_name] = self.safe_read_csv(file_path,f'{csv_name}.csv')

                self.watchlist  = dataframes['watchlist']
                self.watched    = dataframes['watched']
                self.rating     = dataframes['ratings']
                self.reviews    = dataframes['reviews']
                self.profile    = dataframes['profile']
                self.comments   = dataframes['comments']

                # Nettoyage des années
                for attr in ['watchlist', 'watched', 'rating']:
                    setattr(self, attr, clean_year(getattr(self, attr)))

                # Préparation des références
                self.all_movies = pd.DataFrame(self.films_data)
                self.all_movies = clean_year(self.all_movies)

                self.watched_and_watchlist = pd.concat([self.watched, self.watchlist])
                
                # Enrichissement des références
                if exemple is None:
                    movie_return=self.get_films(self.all_movies, self.watched_and_watchlist, my_bar)
                    if movie_return is not None:
                        self.all_movies = movie_return
                    else:
                        erreur_api()

                self.all_movies = self.all_movies.drop_duplicates(subset=['Title', 'Year'])
                self.all_movies = clean_small_films(self.all_movies)
                self.all_movies = bind_categories(self.all_movies)

                # Fichiers spécfiques à l'utilisateur
                # mg = merge = méga fichier avec tous les films et les données intéressantes
                self.watched_mg     = pd.merge(self.watched, self.all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()
                self.watchlist_mg   = pd.merge(self.watchlist, self.all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()
                self.rating_mg      = pd.merge(self.rating, self.all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()

                self.rating_mg['Rating'] = self.rating_mg['Rating'] * 2
                self.rating_mg = clean_imdbr(self.rating_mg)
                self.rating_mg['diff_rating'] = self.rating_mg['Rating'] - self.rating_mg['imdbRating']

                self.radar_stats = compute_radar_stats_for_sheet(
                    self.all_movies, self.watched_mg, self.rating_mg,
                    self.reviews, self.comments, 
                    self.api_handler.get_data_from_sheet("profiles_stats")
                )
                if(st.secrets['prod']==True):
                    self.api_handler.add_profiles_to_stats_sheet(self.profile.iloc[0], self.radar_stats)

            except zipfile.BadZipFile:
                st.session_state["uploader_key"] += 1
                st.warning('This is not a zipfile', icon="⚠️")
                st.session_state["exemple"] = 0
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}", icon="⚠️")

    def safe_read_csv(self, file_path,file_name):
        """ Lit un fichier CSV en gérant les erreurs"""
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            st.session_state["exemple"] = 0
            st.error(f"File {file_name} not found. We need all the csv files of the zipfile", icon="⚠️")
            st.stop()
            return pd.DataFrame()

### 

### Méthodes spécifiques à la gestion des données

    def general_metrics_div(self):
        """ Récupère les stats générales"""
        metrics = [
            (len(self.watched_df.index), " movies", "🎬"),
            (round(computeRuntime(self.watched_df)), " hours", "🕒"),
            (len(self.watched_df['Director'].unique()), " directors", "🎭"),
            (len(self.watchlist_df.index), " movies", "🎯"),
            (round(computeRuntime(self.watchlist_df)), " hours", "⏳"),
        ]

        return self.graph_maker.general_metrics_div(metrics)

    def get_years(self):
        """ Récupère les années de visionnage à partir de la date d'inscription du profil"""
        dateJoined = pd.to_datetime(self.profile['Date Joined'], errors='coerce').dt.year
        dateJoined = int(dateJoined.iloc[0])
        current_year = datetime.now().year
        years = ["Alltime"] + list(sorted(range(dateJoined, current_year + 1), reverse=True))
        return years

    def set_year(self, selected_year):
        """ Définit l'année de visionnage"""
        if selected_year == "Alltime":
            self.watched_df = self.watched_mg
            self.watchlist_df = self.watchlist_mg
            self.rating_df = self.rating_mg
            self.reviews_df = self.reviews
        else:
            selected_year = int(selected_year)
            self.watched_df = extract_year(self.watched_mg, selected_year)
            self.watchlist_df = extract_year(self.watchlist_mg, selected_year)
            self.rating_df = extract_year(self.rating_mg, selected_year)
            self.reviews_df = extract_year(self.reviews, selected_year)
        self.corpus = clean_reviews(self.reviews_df)
        self.year = selected_year

### Gestion des graphiques

    def genre(self, key):
        """ Prépare les data pour le GraphMaker et renvoie le graphique à l'interface"""
        match key:
            case "watched":
                df_genres = self.watched_df[['Name', 'Year','Genre']].dropna()
            case "watchlist":
                df_genres = self.watchlist_df[['Name', 'Year','Genre']].dropna()

        df_genres['Genre'] = df_genres['Genre'].str.split(', ')
        df_genres_exploded = df_genres.explode('Genre')

        return self.graph_maker.graph_genre(df_genres_exploded)
    
    def actor(self, key):
        match key:
            case "watched":
                nb_actor = self.watched_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
            case "watchlist":
                nb_actor = self.watchlist_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
        nb_actor.columns = ['Actors', 'Number of Movies']
        return self.graph_maker.graph_actor(nb_actor)

    def director(self, key):
        match key:
            case "watched":
                nb_real = self.watched_df['Director'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
            case "watchlist":
                nb_real = self.watchlist_df['Director'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
        nb_real.columns = ['Director', 'Number of Movies']
        return self.graph_maker.graph_director(nb_real)

    def famous(self, key):
        match key:
            case "watched":
                movies_rating = self.watched_df.copy()
            case "watchlist":
                movies_rating = self.watchlist_df.copy()
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].replace("N/A", np.nan)
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].replace("", np.nan)
        movies_rating = movies_rating.dropna(subset=['imdbVotes'])
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].astype(str).str.replace(',', '')
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].astype(float)
        bottom_5_votes = movies_rating.sort_values(by='imdbVotes', ascending=True).head(10)
        bottom = bottom_5_votes[['Title', 'imdbVotes']].reset_index(drop=True)
        top_5_votes = movies_rating.sort_values(by='imdbVotes', ascending=False).head(10)
        top = top_5_votes[['Title', 'imdbVotes']].reset_index(drop=True)
        return bottom, top

### CINEPHILE

    def cinephile_graph(self, key):

           # Générer une colonne texte pour le hover
        def make_movies_text(movie_list):
            # Limite l'affichage à 10 films max par genre (pour la lisibilité)
            movies = movie_list[:10]
            movies_text = "<br>".join(f"• {m}" for m in movies)
            if len(movie_list) > 10:
                movies_text += f"<br><span style='color:#888; font-size:12px;'>...and {len(movie_list) - 10} more</span>"
            return movies_text

        match key:
            case "watched":
                habit = self.watched_df.copy()
            case "watchlist":
                habit = self.watchlist_df.copy()

        result = compute_categories(self.all_movies, habit)
        result['Films'] = result['category'].apply(
            lambda x: habit[habit['category'] == x]['Title'].tolist()
        )
        result['MoviesText'] = result['Films'].apply(make_movies_text)

        return self.graph_maker.cinephile_graph(result)

    def cinephile_div(self, key):
        match key:
            case "watched":
                habit = self.watched_df.copy()
                text = "you've watched"
            case "watchlist":
                habit = self.watchlist_df.copy()
                text = "you want to see"
        #result = compute_categories(self.all_movies, habit)

        # on crée un df avec les 4 films les moins vus pour Obscure et les 4 films les plus vus pour Mainstream
        obscure_films = habit.sort_values('imdbVotes', ascending=True).head(4)
        mainstream_films = habit.sort_values('imdbVotes', ascending=False).head(4)

        return self.graph_maker.two_div_four_films(mainstream_films, obscure_films, "most popular", "least popular", text)

### 

### DECADE

    def decade_graph(self, key):
        match key:
            case "watched":
                df = self.watched_df.copy()
            case "watchlist":
                df = self.watchlist_df.copy()

        df = df.dropna(subset=['Year']).copy()
        df['Year'] = df['Year'].astype(int)

        # Calcul du bin de 5 ans
        df['FiveYearBin'] = df['Year'].apply(lambda y: f"{(y//5)*5}-{(y//5)*5+4}")

        # Groupby sur la tranche de 5 ans
        grouped = (
            df.groupby('FiveYearBin')
            .agg(Number=('Title', 'count'), Movies=('Title', list))
            .reset_index()
            .sort_values('FiveYearBin')
        )
        grouped['MoviesText'] = grouped['Movies'].apply(make_movies_text)

        return self.graph_maker.graph_decade(grouped)
    
    def decade_div(self, key):
        match key:
            case "watched":
                df_decade = self.watched_df.copy()
                text = "you've watched"
            case "watchlist":
                df_decade = self.watchlist_df.copy()
                text = "you want to see"
        df_decade=df_decade.sort_values('Year', ascending=True)
        oldest_films = df_decade.head(4)
        newest_films = df_decade.tail(4)

        return self.graph_maker.two_div_four_films(oldest_films, newest_films, "oldest", "most recent", text)

### 

    def runtime_bar(self, key):
        match key:
            case "watched":
                df = self.watched_df.copy()
            case "watchlist":
                df = self.watchlist_df.copy()
        df = df[(df['Runtime'] >= 10) & (df['Runtime'] <= 300)]
        #bins = list(range(df['Runtime'].min(), df['Runtime'].max() + 10, 10))  # Bins de 10 minutes de 0 à 300 minutes
        bins = list(range(10, 301, 10))
        labels = [f'{i}-{i+9}' for i in bins[:-1]]
        df['RuntimeBin'] = pd.cut(df['Runtime'], bins=bins, labels=labels, right=True, include_lowest=True)
        runtime_counts = df['RuntimeBin'].value_counts().sort_index().reset_index()
        runtime_counts.columns = ['RuntimeBin', 'Count']
        return self.graph_maker.graph_runtime_bar(df)

    def mapW(self, key):
        match key:
            case "watched":
                df_country = self.watched_df.copy()
            case "watchlist":
                df_country = self.watchlist_df.copy()
        df_country['Country'] = df_country['Country'].dropna().str.split(', ')
        df_genres_exploded = df_country.explode('Country')
        genre_counts = df_genres_exploded['Country'].value_counts().reset_index()
        countries = {country.name: country.alpha_3 for country in pycountry.countries}
        genre_counts['code'] = genre_counts['Country'].map(countries)
        return self.graph_maker.graph_mapW(genre_counts)

    def mapW_div(self, country,key):
        """ Affiche 4 films d'un pays sélectionné sur la carte"""
        match key:
            case "watched":
                df_country = self.watched_df.copy()
                text = "you watched from "
            case "watchlist":
                df_country = self.watchlist_df.copy()
                text = "you want to watch from "
        df_country['Country'] = df_country['Country'].dropna().str.split(', ')
        df_genres_exploded = df_country.explode('Country')
        countries = {country.name: country.alpha_3 for country in pycountry.countries}
        df_genres_exploded['code']=df_genres_exploded['Country'].map(countries)
        df_genres_exploded=df_genres_exploded[df_genres_exploded['code']==country]
        if(len(df_genres_exploded)>4):
            top_4 = df_genres_exploded.sample(4,replace=False)
        else:
            top_4 = df_genres_exploded.sample(4,replace=True)
        text = text+top_4.Country.iloc[0]
        return self.graph_maker.one_div_four_films(top_4, text)
    
    def diff_rating(self):
        sur_note = self.rating_df.sort_values(by=['diff_rating'],ascending=False)
        sur_note = sur_note.head(10).reset_index(drop=True)

        sous_note = self.rating_df.sort_values(by=['diff_rating'])
        sous_note = sous_note.head(10).reset_index(drop=True)
        return sur_note[['Name','Rating','imdbRating','diff_rating']], sous_note[['Name','Rating','imdbRating','diff_rating']]
    
    def diff_rating_test(self,key):
        match key:
            case "overrated":
                df = self.rating_df.sort_values(by=['diff_rating'],ascending=False)
                df = df.head(10).reset_index(drop=True)
                text= "you have most overrated"
            case "underrated":
                df = self.rating_df.sort_values(by=['diff_rating'])
                df = df.head(10).reset_index(drop=True)
                text= "you have most underrated"
        div= self.graph_maker.two_div_five_films(df.head(5), df.tail(5), text)
        return div
    def rating_director(self):
        nb_real = self.rating_df['Director'].value_counts().head(25)
        df_top_directors = self.rating_df[self.rating_df['Director'].isin(nb_real.index)]
        nb_films_par_director = df_top_directors['Director'].value_counts().reset_index()
        nb_films_par_director.columns = ['Director', 'Number of movie']
        mean_rating = df_top_directors.groupby('Director')['Rating'].mean().rename('Moyenne_Rating').reset_index()
        mean_rating.columns = ['Director', 'Moyenne_Rating']
        df_plot = pd.merge(nb_films_par_director, mean_rating, on='Director')
        return self.graph_maker.graph_rating_director(df_plot, nb_films_par_director)

    def rating_actor(self):
        nb_actor = self.rating_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25)
        top_actors = nb_actor.index

        df_exploded = self.rating_df.dropna(subset=['Actors']).copy()
        df_exploded['Actor'] = df_exploded['Actors'].str.split(', ')
        df_exploded = df_exploded.explode('Actor')

        df_top_actors = df_exploded[df_exploded['Actor'].isin(top_actors)]

        nb_films_par_actor = df_top_actors['Actor'].value_counts().reset_index()
        nb_films_par_actor.columns = ['Actor', 'Nb_Films']

        mean_rating_actor = df_top_actors.groupby('Actor')['Rating'].mean().reset_index()
        mean_rating_actor.columns = ['Actor', 'Moyenne_Rating']

        df_actor_plot = pd.merge(nb_films_par_actor, mean_rating_actor, on='Actor')
        return self.graph_maker.graph_rating_actor(df_actor_plot)

    def genre_rating(self):
        rating_local=self.rating_df.copy()
        rating_local['Genre'] = rating_local['Genre'].dropna().str.split(', ')
        df_genres_exploded = rating_local.explode('Genre')
        genre_counts = df_genres_exploded['Genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Nombre de films']

        mean_rating_genre = df_genres_exploded.groupby('Genre')['Rating'].mean().reset_index()
        mean_rating_genre.columns = ['Genre', 'Moyenne_Rating']

        df_genre_plot = pd.merge(genre_counts, mean_rating_genre, on='Genre')
        return self.graph_maker.graph_genre_rating(df_genre_plot)

    def comparaison_rating(self):
        # Groupby pour compter les valeurs dans 'Rating'
        rate = self.rating_df.copy()
        rate['imdbRating'] = pd.to_numeric(rate['imdbRating'], errors='coerce')
        rate = rate.dropna(subset=['imdbRating'])
        rate['imdbRating'] = (rate['imdbRating'] * 2).round() / 2
        rate = rate.groupby('imdbRating').size().reset_index(name='Number of movie')
        return self.graph_maker.graph_comparaison_rating(rate, self.rating_df)

    # TODO: séparer la logique de génération de wordcloud
    def generate_wordcloud(self):
        if not self.corpus.empty:
            stopwords = set(get_stop_words('fr')) | set(get_stop_words('en'))
            wordcloud = WordCloud(stopwords=stopwords,width=800, height=400, background_color="black",max_words=120)
            text = " ".join(self.corpus)
            wc=wordcloud.generate(text)
            return self.graph_maker.graph_generate_wordcloud(wc)

    def radar_graph(self):
        fig = self.graph_maker.graph_radar(self.radar_stats)
        return fig

    def waffle(self,year):
        df=self.watched_mg.copy()
        df_count = df.groupby('Date').size().reset_index(name='count')
        debut,fin=get_year_bounds(year)
        debut=pd.to_datetime(debut)
        fin=pd.to_datetime(fin)
        df_count['Date']=pd.to_datetime(df_count['Date'])
        df_year=df_count[df_count['Date'].between(debut,fin)]
        df_year.columns=['date','count']

        all_dates = pd.date_range(start=debut, end=fin, freq='D').normalize()

        df_year_mg = pd.merge(
            pd.DataFrame({'date': all_dates}),
            df_year,
            on='date',
            how='left'
        ).fillna({'count': 0, 'films_list': ''})
        df_year_mg['count']=df_year_mg['count'].astype(int)


        month_pos, weekdays, weeknumber = get_date_coordinates(
        data=df_year_mg,
        x='date'
        )
        return self.graph_maker.waffle(df_year_mg, month_pos, weekdays, weeknumber)

###
