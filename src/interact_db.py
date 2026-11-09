import database as db
from process_data import GitHubUserRepo, UserStats
import sqlalchemy as sa
import sqlalchemy.orm as orm

def save_user_profile(session: orm.Session, user_stats: UserStats, git_user_repos: list[GitHubUserRepo]) -> None:
    """
    Save the user and their statistics to the database
    """
    user = transform_data_to_db_format(user_stats, git_user_repos)
    existing_user = session.scalar(sa.select(db.User).where(db.User.id == user.id))

    if existing_user:
        # Update existing user in the database
        existing_user.username = user.username
        existing_user.repos = user.repos
        existing_user.total_repos = user.total_repos
        existing_user.total_stars = user.total_stars
        existing_user.total_commits = user.total_commits
        existing_user.average_stars_per_repo = user.average_stars_per_repo
        existing_user.most_used_language = user.most_used_language
    else:
        # Add new user and their repos to the database
        session.add(user)

    # Commit the changes to the database
    session.commit()

def transform_data_to_db_format(user_stats: UserStats, user_repos: list[GitHubUserRepo]) -> db.User:
    """
    Transform the Pydantic models to a database-compatible format (User model)
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

    return db.User(
        id=user_stats.id,
        username=user_stats.username,
        repos = db_repos,
        total_repos=user_stats.total_repos,
        total_stars=user_stats.total_stars,
        total_commits=user_stats.total_commits,
        average_stars_per_repo=user_stats.average_stars_per_repo,
        most_used_language=user_stats.most_used_language
    )
