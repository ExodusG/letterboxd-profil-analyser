from sqlalchemy import String, Integer
from sqlalchemy.orm import  Mapped, mapped_column

from src.db.database import Base

class Error(Base):
    __tablename__ = "errors"

    # Clé primaire composite
    title: Mapped[str] = mapped_column(
        String(500),
        primary_key=True
    )

    year: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    nb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )