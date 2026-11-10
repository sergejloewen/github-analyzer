import requests
import process_data as pd
import database as db
import interact_db as iDB
from fastapi import FastAPI, Depends, HTTPException
import schemas as res
from sqlalchemy.orm import Session
import sqlalchemy as sa

app = FastAPI()

#TODO add potentially more error handling for API endpoints and tests

@app.get("/")
def read_root():
    return {"message": "Welcome to the GitHub Analyzer API!", "status": "API is running successfully."}

@app.get("/api/users", response_model=list[res.UserResponse])
def get_users(session: Session = Depends(db.get_db)):
    """
    Get all users from the database
    """
    users = session.scalars(sa.select(db.User)).all()
    return users

@app.get("/api/users/{username}", response_model=res.UserResponse)
def get_user(username: str, session: Session = Depends(db.get_db)):
    """
    Get a specific user and their statistics + repositories from the database by username
    """
    # Fetch user ID from GitHub API to ensure the user exists 
    # and gets the right user from the database, as the username is not unique in the database 
    # but the user ID is.
    user_id = pd.fetch_user_id(username)

    # If the user ID is None, it means the user does not exist on GitHub, so we raise a 404 error.
    if user_id is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on GitHub.")

    user = session.scalar(sa.select(db.User).where(db.User.id == user_id))

    # If the user is not found in the database, raise a 404 error.
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found in the database.")

    return user

@app.get("/api/repos", response_model=list[res.RepoResponse])
def get_repos(session: Session = Depends(db.get_db)):
    """
    Get all repositories from the database
    """
    repos = session.scalars(sa.select(db.Repo)).all()
    return repos

@app.get("/api/repos/{repo_id}", response_model=res.RepoResponse)
def get_repo(repo_id: int, session: Session = Depends(db.get_db)):
    """
    Get a specific repository from the database by its ID
    ID is unique for each repository, but name can be the same for different repositories
    if it is owned by different users, so we use the ID to get the right repository.
    """
    repo = session.scalar(sa.select(db.Repo).where(db.Repo.id == repo_id))

    # If the repository is not found in the database, raise a 404 error.
    if repo is None:
        raise HTTPException(status_code=404, detail=f"Repository with ID '{repo_id}' not found in the database.")

    return repo

@app.post("/api/analyze/{username}", response_model=res.UserResponse)
def save_user(username: str, session: Session = Depends(db.get_db)):
    """
    Save a new user, their stats and repositories by fetching data from the GitHub API and saving it to the database
    """
    # Fetch user ID and repositories from GitHub API
    user_id = pd.fetch_user_id(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found on GitHub.")
    
    raw_data = pd.fetch_user_repos(username)
    user_repos = pd.analyze_repos(raw_data)
    stats = pd.calculate_stats(user_repos, user_id, username)

    # Save the user, their statistics and repositories to the database
    iDB.save_user_profile(session, stats, user_repos)

    # Retrieve the saved user from the database to return as a response
    db_user = session.scalar(sa.select(db.User).where(db.User.id == user_id))

    return db_user


# def main():
#     # checking if the Github API is reachable
#     githubAPI = requests.get("https://api.github.com")
#     print(githubAPI.status_code)

#     username = pd.get_user_input()
#     user_id = pd.fetch_user_id(username)
#     raw_data = pd.fetch_user_repos(username)
#     user_repos = pd.analyze_repos(raw_data)
#     stats = pd.calculate_stats(user_repos, user_id, username)

#     # commented out as not needed for future implementation, but can be used for visualization of the data
#     # in Console for testing and debugging purposes. Can be uncommented if needed.
#     # pd.visualize_repos(user_repos, stats)  

#     # Save the user, their statistics and repositories to the database
#     with db.get_db() as session:
#         iDB.save_user_profile(session, stats, user_repos)

# if __name__ == "__main__":
#     main()