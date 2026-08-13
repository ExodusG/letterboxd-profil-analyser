import json
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, select
from src.db.models.user_stats import UserStats
from src.db.database import get_session


def get_user_stats():

    session = get_session()

    try:

        result=session.query(UserStats).all()
        df_result = pd.DataFrame([
        {
            column.name: getattr(movie, column.name)
            for column in UserStats.__table__.columns
        }
        for movie in result
        ])

        return df_result
    finally:
        session.close()

def get_global_stats():

    session = get_session()

    try:
        first_row = (
            select(UserStats.ratio_par_genre)
            .order_by(UserStats.id)
            .limit(1)
            .scalar_subquery()
        )

        stmt = select(
            func.avg(UserStats.nb_films_vus).label("nb_films_vus"),
            func.avg(UserStats.ratio_peu_vus).label("ratio_peu_vus"),
            func.avg(UserStats.moyenne_diff_rating).label(
                "moyenne_diff_rating"
            ),
            func.avg(UserStats.nb_interactions).label(
                "nb_interactions"
            ),
            first_row.label("ratio_par_genre"),
        )

        result = session.execute(stmt).mappings().one()

        return dict(result)

    finally:
        session.close()

def clean_genre(value):
    if isinstance(value, str):

        value = value.strip()

        if not value:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            print(
                "Erreur JSON dans ratio_par_genre :"
            )
            print(value)
            raise e

    return None

def add_profile_to_stats(profile, radar_stats):

    session = get_session()

    try:

        profile_id = profile["Username"]

        values = {
            "id": profile_id,
            "consommateur": radar_stats["Consommateur"],
            "explorateur": radar_stats["Explorateur"],
            "consensuel": radar_stats["Consensuel"],
            "eclectique": radar_stats["Éclectique"],
            "actif": radar_stats["Actif"],
            "nb_films_vus": radar_stats["nb_films_vus"],
            "ratio_peu_vus": radar_stats["ratio_peu_vus"],
            "moyenne_diff_rating": radar_stats[
                "moyenne_diff_rating"
            ],
            "ratio_par_genre": clean_genre(radar_stats[
                "ratio_par_genre"
            ]),
            "nb_interactions": radar_stats[
                "nb_interactions"
            ],
            "nb_passages": 1,
        }

        stmt = insert(UserStats).values(**values)

        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "consommateur": stmt.excluded.consommateur,
                "explorateur": stmt.excluded.explorateur,
                "consensuel": stmt.excluded.consensuel,
                "eclectique": stmt.excluded.eclectique,
                "actif": stmt.excluded.actif,
                "nb_films_vus": stmt.excluded.nb_films_vus,
                "ratio_peu_vus": stmt.excluded.ratio_peu_vus,
                "moyenne_diff_rating": (
                    stmt.excluded.moyenne_diff_rating
                ),
                "ratio_par_genre": stmt.excluded.ratio_par_genre,
                "nb_interactions": stmt.excluded.nb_interactions,

                # Ancienne valeur + 1
                "nb_passages": UserStats.nb_passages + 1,
            }
        )

        session.execute(stmt)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()