import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from src.db.database import get_session
from src.db.models import Error


def add_movies_to_count(df):

    if df.empty:
        return
    # On garde uniquement les colonnes nécessaires
    df = df[["Name", "Year"]].rename(
        columns={
            "Name": "title",
            "Year": "year"
        }
    )

    # Nettoyage
    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df = df.dropna(subset=["title", "year"])

    df["year"] = df["year"].astype(int)

    records = df.to_dict(orient="records")

    session = get_session()

    try:

        stmt = insert(Error).values(records)

        stmt = stmt.on_conflict_do_update(
            index_elements=[
                "title",
                "year"
            ],
            set_={
                "nb": Error.nb + stmt.excluded.nb
            }
        )

        session.execute(stmt)
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()