from sqlalchemy.dialects.postgresql import insert
from src.db.database import get_session
from src.db.models import Error


def add_error(records):

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