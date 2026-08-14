from typing import Optional 
from datetime import date 
from sqlalchemy import String, Integer, Float, Boolean, JSON, TEXT 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.db.database import Base
#TODO have a better schema for this class (at least 0NF)
class Movie(Base):
    __tablename__ = "movies"

    # Clé primaire composite
    title: Mapped[str] = mapped_column(
        String(500),
        primary_key=True
    )

    year: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    rated: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    released: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    runtime: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    genre: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    director: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    writer: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    actors: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    plot: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    country: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    awards: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    poster: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    # Liste de dictionnaires :
    # [
    #     {"Source": "Internet Movie Database", "Value": "6.8/10"},
    #     {"Source": "Rotten Tomatoes", "Value": "93%"}
    # ]
    ratings: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True
    )

    metascore: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    imdbRating: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    imdbVotes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    imdbID: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    dvd: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    boxOffice: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    production: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    website: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True
    )

    response: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    totalSeasons: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    error: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    column_ep_1: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    column_ep_2: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )