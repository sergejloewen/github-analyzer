from typing import Optional
from pydantic import BaseModel

class RepoResponse(BaseModel):
    """
    Response model for a GitHub repository.
    """
    model_config = {
            "from_attributes": True,  # Allow model to be created from ORM objects
        }

    id: int
    owner_id: int
    name: str
    language: Optional[str] = None
    stars: int
    description: Optional[str] = None

class UserResponse(BaseModel):
    """
    Response model for a GitHub user.
    """
    model_config = {
        "from_attributes": True,  # Allow model to be created from ORM objects
    }

    id: int
    username: str
    repos: list[RepoResponse]
    total_repos: int
    total_stars: int
    average_stars_per_repo: float
    most_used_language: Optional[str] = None