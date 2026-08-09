from sqlalchemy import select, tuple_,func
from src.db.database import get_session
from src.db.models import Movie
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
BATCH_SIZE = 100

def get_movies(limit=100):

    session = get_session()

    try:

        return (
            session.query(Movie)
            .limit(limit)
            .all()
        )

    finally:

        session.close()


def get_all_movies(df):
    """
    Sépare le DataFrame entre :
    - les films déjà présents en base
    - les films absents de la base

    Le DataFrame doit contenir :
    - Title
    - Year
    """

    if df.empty:
        return df.copy(), df.copy()


    df["Year"] = pd.to_numeric(
    df["Year"],
        errors="coerce"
    )
    # On récupère uniquement les couples Title / Year
    movie_keys = list(
        df[["Name", "Year"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    session = get_session()

    try:
        stmt = (
            select(Movie)
            .where(
                tuple_(
                    Movie.title,
                    Movie.year
                ).in_(movie_keys)
            )
        )

        result = session.execute(stmt)

        df_result = pd.DataFrame([
        {
            column.name: getattr(movie, column.name)
            for column in Movie.__table__.columns
        }
        for movie in result.scalars()
        ])

    finally:
        session.close()

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

def clean_value(value):
    """
    Convertit les NaN/NaT Pandas en None.
    Conserve les listes et dictionnaires.
    """

    if value is None:
        return None

    if isinstance(value, (list, dict)):
        return value

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value

def save_movies(df):
    if df.empty: 
        return 0 
    df = df.copy()
    print(df)
    df.columns = df.columns.str[:1].str.lower() + df.columns.str[1:]
    model_columns = { column.name for column in Movie.__table__.columns } 
    df = df[ [ column for column in df.columns if column in model_columns ] ].copy()
    session = get_session()
    inserted_count = 0
    print("bonjour")
    print(df)
    try:

        for start in range(
            0,
            len(df),
            BATCH_SIZE
        ):
            batch = df[
                start:start + BATCH_SIZE
            ]

            records = batch.to_dict(
                orient="records"
            )

            # Nettoyage des valeurs
            records = [
                {
                    key: clean_value(value)
                    for key, value in record.items()
                }
                for record in records
            ]

            stmt = (
                insert(Movie)
                .values(records)
                .on_conflict_do_nothing(
                    index_elements=[
                        "title",
                        "year"
                    ]
                )
            )
            result = session.execute(stmt)
            inserted_count += result.rowcount
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return inserted_count

def compute_quantiles():
    """
    Calcule les quantiles 5%, 20% et 50% de imdbVotes
    directement dans PostgreSQL.

    Retourne :
        q1, q2, q3
    """

    session = get_session()

    try:

        stmt = select(
            func.percentile_cont(0.05)
                .within_group(Movie.imdbVotes).label("q1"),

            func.percentile_cont(0.20)
                .within_group(Movie.imdbVotes).label("q2"),

            func.percentile_cont(0.50)
                .within_group(Movie.imdbVotes).label("q3"),
        ).where(
            Movie.imdbVotes.is_not(None)
        )

        result = session.execute(stmt).one()

        q1 = result.q1
        q2 = result.q2
        q3 = result.q3

        return q1, q2, q3

    finally:
        session.close()

