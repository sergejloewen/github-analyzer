import database as db
from process_data import GitHubUserRepo, UserStats
import sqlalchemy as sa
import sqlalchemy.orm as orm

#TODO add potential more error handling for database operations, such as connection issues or integrity errors.
#TODO add tests for the database operations, including saving and retrieving user profiles and repositories.

def save_user_profile(session: orm.Session, user_stats: UserStats, git_user_repos: list[GitHubUserRepo]) -> None:
    """
    Save the user, their repositories, and their statistics to the database
    if the user already exists, update their information and repositories; otherwise, create a new user entry.
    """
    # transform repo list to database-compatible format
    db_repos = transform_repos_to_db_format(git_user_repos)
    # check if the user already exists in the database
    existing_user = session.scalar(sa.select(db.User).where(db.User.id == user_stats.id))

    if existing_user:
        # Update existing user in the database
        existing_user.username = user_stats.username
        existing_user.repos = db_repos # update the repos relationship with the new list of repos
        existing_user.total_repos = user_stats.total_repos
        existing_user.total_stars = user_stats.total_stars
        existing_user.total_commits = user_stats.total_commits
        existing_user.average_stars_per_repo = user_stats.average_stars_per_repo
        existing_user.most_used_language = user_stats.most_used_language
    else:
        # create new user from pydantic models and add to the database
        new_user = db.User(
            id=user_stats.id,
            username=user_stats.username,
            repos=db_repos,
            total_repos=user_stats.total_repos,
            total_stars=user_stats.total_stars,
            total_commits=user_stats.total_commits,
            average_stars_per_repo=user_stats.average_stars_per_repo,
            most_used_language=user_stats.most_used_language
        )

        session.add(new_user)

    # Commit the changes to the database
    session.commit()

def transform_repos_to_db_format(user_repos: list[GitHubUserRepo]) -> list[db.Repo]:
    """
    Transform the Pydantic repo model to a database-compatible format (User model)
    """
    db_repos = []
    for repo in user_repos:
        db_repo = db.Repo(
            id=repo.id,
            owner_id=repo.owner_id,
            name=repo.name,
            language=repo.language,
            stars=repo.stars,
            commits=repo.commits,
            description=repo.description
        )
        db_repos.append(db_repo)

    return db_repos
