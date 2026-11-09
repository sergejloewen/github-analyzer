from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import Optional

engine = create_engine('sqlite+pysqlite:///github_data.db', echo=True)
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

def get_db():
    with SessionLocal() as session:
        yield session

Base.metadata.create_all(bind=engine)
