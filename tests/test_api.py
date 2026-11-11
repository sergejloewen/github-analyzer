from src import database as db


def test_read_root(client):
    """
    Test the root endpoint of the FastAPI application.
    This test checks if the root endpoint ("/") returns a successful response with the expected message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the GitHub Analyzer API!",
                                "status": "API is running successfully."}

def test_get_users_empty(client):
    """
    Test the /api/users endpoint when the database is empty.
    This test checks if the endpoint returns an empty list when there are no users in the database.
    """
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []

def test_get_repos_empty(client):
    """
    Test the /api/repos endpoint when the database is empty.
    This test checks if the endpoint returns an empty list when there are no repositories in the database.
    """
    response = client.get("/api/repos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_specific_repo_not_found(client):
    """
    Test the /api/repos/{repo_id} endpoint when the specified repository does not exist.
    This test checks if the endpoint returns a 404 status code and the expected error message when the repository is not found.
    """
    non_existent_repo_id = 9999  # Assuming this ID does not exist in the test database
    response = client.get(f"/api/repos/{non_existent_repo_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Repository with ID '{non_existent_repo_id}' not found in the database."}

def test_get_specific_repo_success(client, db_session):
    """
    Test the /api/repos/{repo_id} endpoint when the specified repository exists.
    This test checks if the endpoint returns a successful response with the expected repository data.
    """
    # Create a test user and repository in the database
    test_user = db.User(username="testuser", total_repos=1, total_stars=10, total_commits=5,
                        average_stars_per_repo=10.0, most_used_language="Python")
    db_session.add(test_user)
    db_session.flush()

    test_repo = db.Repo(owner_id=test_user.id, name="testrepo", language="Python",
                        stars=10, commits=5, description="Test repository")
    db_session.add(test_repo)
    db_session.commit()

    # Now test the endpoint with the created repository ID
    response = client.get(f"/api/repos/{test_repo.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": test_repo.id,
        "owner_id": test_user.id,
        "name": "testrepo",
        "language": "Python",
        "stars": 10,
        "commits": 5,
        "description": "Test repository"
    }