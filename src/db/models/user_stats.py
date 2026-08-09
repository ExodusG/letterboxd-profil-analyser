from typing import Optional

from sqlalchemy import Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class UserStats(Base):
    __tablename__ = "user_stats"

    # Identifiant unique de l'utilisateur
    id: Mapped[str] = mapped_column(
        primary_key=True
    )

    consommateur: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    explorateur: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    consensuel: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    eclectique: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    actif: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    nb_films_vus: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    ratio_peu_vus: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    moyenne_diff_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    # Exemple :
    # {
    #     "Action": 0.5,
    #     "Drama": 0.477,
    #     "Adventure": 0.438
    # }
    ratio_par_genre: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    nb_interactions: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    nb_passages: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
