from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import Optional
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    # this default value should ideally be hidden, but as this is a local development environment, 
    # it is okay to have it here for now.
    "postgresql+psycopg://postgres:meingeheimnis@localhost:5432/github_analyzer" 
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Define the base class for declarative models
class Base(DeclarativeBase):
    pass

# define the Repo and User models
class Repo(Base):
    __tablename__ = 'repos'

    id: Mapped [int] = mapped_column(primary_key=True)
    owner_id: Mapped [int] = mapped_column(ForeignKey('users.id'))
    owner: Mapped ["User"] = relationship(back_populates="repos")
    name: Mapped [str]
    language: Mapped [str]
    stars: Mapped [int]
    commits: Mapped [int]
    description: Mapped[Optional[str]]

class User(Base):
    __tablename__ = 'users'

    id: Mapped [int] = mapped_column(primary_key=True)
    username: Mapped [str]
    repos: Mapped [list[Repo]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    total_repos: Mapped [int]
    total_stars: Mapped [int]
    total_commits: Mapped [int]
    average_stars_per_repo: Mapped [float]
    most_used_language: Mapped [str]

# Context manager to handle database sessions
# Commented out as we go from the app being used in CLI to being used as an API, 
# and the API will handle the database sessions differently.
# @contextmanager
# def get_db():
#     with SessionLocal() as session:
#         yield session

def get_db():
    """
    Get a database session for interacting with the database.
    This function is used as a dependency in FastAPI routes to provide a session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
