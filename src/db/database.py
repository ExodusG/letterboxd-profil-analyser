import streamlit as st

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = URL.create(
    "postgresql+psycopg",
    username="exoduss",
    password="admin",
    host="localhost",
    database="movie",
)


@st.cache_resource
def get_engine():
    """
    Crée l'engine SQLAlchemy une seule fois.
    Streamlit le met en cache entre les reruns.
    """

    return create_engine(
        DATABASE_URL,
        echo=False,
    )


@st.cache_resource
def get_session_factory():
    """
    Crée le sessionmaker une seule fois.
    """

    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


def get_session():
    """
    Crée une nouvelle session SQLAlchemy.
    La session elle-même n'est PAS mise en cache.
    """

    return get_session_factory()()


class Base(DeclarativeBase):
    pass
