import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from src import interact_db as idb
from src import database as db
from src.process_data import GitHubUserRepo, UserStats
from tests.conftest import db_session

def test_transform_repos_to_db_format(sample_users):
    """
    Test the transformation of GitHubUserRepo instances to database-compatible Repo instances.
    """
    for userstats, user_repos in sample_users:
        db_repos = idb.transform_repos_to_db_format(user_repos)
        assert len(db_repos) == len(user_repos)
        for db_repo, user_repo in zip(db_repos, user_repos):
            assert db_repo.id == user_repo.id
            assert db_repo.owner_id == user_repo.owner_id
            assert db_repo.name == user_repo.name
            assert db_repo.language == user_repo.language
            assert db_repo.stars == user_repo.stars
            assert db_repo.commits == user_repo.commits
            assert db_repo.description == user_repo.description
    assert isinstance(db_repos[0], db.Repo)  # Check if the first transformed repo is an instance of db.Repo

def test_save_new_user_profile(db_session, sample_users):
    """
    Test saving a new user profile to the database.
    """

    idb.save_user_profile(db_session, sample_users[0][0], sample_users[0][1])
    # Verify that the user was saved correctly
    saved_user = db_session.scalar(sa.select(db.User).where(db.User.id == sample_users[0][0].id))
    assert saved_user is not None
    assert saved_user.username == sample_users[0][0].username
    assert saved_user.total_repos == sample_users[0][0].total_repos
    assert saved_user.total_stars == sample_users[0][0].total_stars
    assert saved_user.total_commits == sample_users[0][0].total_commits
    assert saved_user.average_stars_per_repo == sample_users[0][0].average_stars_per_repo
    assert saved_user.most_used_language == sample_users[0][0].most_used_language

def test_update_existing_user_profile(db_session, sample_users):
    """
    Test updating an existing user profile in the database.
    Checks if the user information and repositories are updated correctly 
    and there are no duplicate entries for the same user or ForeignKey constraint violations.
    """
    # First, save the initial user profile
    idb.save_user_profile(db_session, sample_users[0][0], sample_users[0][1])

    # Modify the user stats and repos for update
    updated_user_stats = UserStats(
        id=sample_users[0][0].id,
        username="updateduser",
        total_repos=3,
        total_stars=15,
        total_commits=10,
        average_stars_per_repo=5.0,
        most_used_language="JavaScript"
    )
    updated_user_repos = [
        GitHubUserRepo(id=103, owner_id=sample_users[0][0].id, name="repo3", language="JavaScript", stargazers_count=5, commits=4, description="Updated repo 3")
    ]

    # Update the existing user profile
    idb.save_user_profile(db_session, updated_user_stats, updated_user_repos)

    # Verify that the user was updated correctly
    saved_user = db_session.scalar(sa.select(db.User).where(db.User.id == updated_user_stats.id))
    assert saved_user is not None
    assert saved_user.username == updated_user_stats.username
    assert saved_user.total_repos == updated_user_stats.total_repos
    assert saved_user.total_stars == updated_user_stats.total_stars
    assert saved_user.total_commits == updated_user_stats.total_commits
    assert saved_user.average_stars_per_repo == updated_user_stats.average_stars_per_repo
    assert saved_user.most_used_language == updated_user_stats.most_used_language
    assert len(saved_user.repos) == len(updated_user_repos)  # Ensure the number of repos is updated correctly
