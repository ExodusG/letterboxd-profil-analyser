import pandas as pd
from src.db.queries.qr_movie import *


class MovieService:
    def get_movie_not_dl(self):
        return pd.read_csv("static/movie_not_dl.csv")

    def get_movie_db(self, df):
        if df.empty:
            return df.copy(), df.copy()


        df["Year"] = pd.to_numeric(
        df["Year"],
            errors="coerce"
        )

        df_result=get_all_movies(df)
        df_missing = (
            df.merge(
                df_result[["title", "year"]],
                left_on=["Name", "Year"],
                right_on=["title", "year"],
                how="left",
                indicator=True
            )
        )

        df_missing = df_missing[
            df_missing["_merge"] == "left_only"
        ].drop(
            columns=["title", "year", "_merge"]
        )
        
        return df_result, df_missing

    
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

        df["Year"] = pd.to_numeric(
            df["Year"],
            errors="coerce"
        )
        df = df.dropna(subset=["Year"])
        df["Metascore"] = pd.to_numeric(
            df["Metascore"],
            errors="coerce"
        )

        df["imdbRating"] = pd.to_numeric(
            df["imdbRating"],
            errors="coerce"
        )

        if df.empty: 
                return 0 
        df = df.copy()
    
        df.columns = df.columns.str[:1].str.lower() + df.columns.str[1:]
        model_columns = { column.name for column in Movie.__table__.columns } 
        df = df[ [ column for column in df.columns if column in model_columns ] ].copy()
        
        return save_movies(df)
    
    def get_quantile(self):
        return compute_quantiles()