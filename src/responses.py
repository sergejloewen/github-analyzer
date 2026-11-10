from typing import Optional
from pydantic import BaseModel

class RepoResponse(BaseModel):
    """
    Response model for a GitHub repository.
    """
    id: int
    owner_id: int
    name: str
    language: Optional[str] = None
    stars: int
    commits: int
    description: Optional[str] = None

class UserResponse(BaseModel):
    """
    Response model for a GitHub user.
    """
    id: int
    username: str
    repos: list[RepoResponse]
    total_repos: int
    total_stars: int
    total_commits: int
    average_stars_per_repo: float
    most_used_language: Optional[str] = None