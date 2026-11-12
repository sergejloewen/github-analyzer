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

def test_get_user_no_repos(client, db_session, sample_users, sample_user_responses):
    """
    Test the /api/users endpoint for a user with no repositories.
    This test checks if the endpoint returns the expected user data when the user exists in the database but has no repositories.
    """
    # Save a sample user with no repositories to the database
    user_stats, user_repos = sample_users[2]  # Assuming this is the user with no repos
    db_user = db.User(
        id=user_stats.id,
        username=user_stats.username,
        total_repos=user_stats.total_repos,
        total_stars=user_stats.total_stars,
        total_commits=user_stats.total_commits,
        average_stars_per_repo=user_stats.average_stars_per_repo,
        most_used_language=user_stats.most_used_language
    )
    db_session.add(db_user)
    db_session.commit()

    # Now test the endpoint for this user
    response = client.get(f"/api/users")
    assert response.status_code == 200
    assert len(response.json()) == 1  # Ensure there are 1 user in the response
    assert response.json()[0]["id"] == sample_user_responses[2].id  # Assuming this is the expected response for the user with no repos
    assert response.json()[0]["username"] == sample_user_responses[2].username
    assert response.json()[0]["total_repos"] == sample_user_responses[2].total_repos
    assert response.json()[0]["total_stars"] == sample_user_responses[2].total_stars
    assert response.json()[0]["total_commits"] == sample_user_responses[2].total_commits
    assert response.json()[0]["average_stars_per_repo"] == sample_user_responses[2].average_stars_per_repo
    assert response.json()[0]["most_used_language"] == sample_user_responses[2].most_used_language
    assert response.json()[0]["repos"] == []  # Ensure the repos list is empty

def test_get_users_with_data(client, db_session, sample_users, sample_user_responses):
    """
    Test the /api/users endpoint when the database contains user data.
    This test checks if the endpoint returns the expected list of users when there are users in the database.
    """
    # Save sample users to the database
    for user_stats, user_repos in sample_users:
        db_user = db.User(
            id=user_stats.id,
            username=user_stats.username,
            total_repos=user_stats.total_repos,
            total_stars=user_stats.total_stars,
            total_commits=user_stats.total_commits,
            average_stars_per_repo=user_stats.average_stars_per_repo,
            most_used_language=user_stats.most_used_language
        )
        db_session.add(db_user)
        db_session.flush()  # Flush to get the user ID for foreign key relationships

        # Save associated repositories
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
            db_session.add(db_repo)

    db_session.commit()

    # Now test the endpoint
    response = client.get("/api/users")
    assert response.status_code == 200
    users_data = response.json()
    assert len(users_data) == len(sample_users)
    assert users_data == [user_response.model_dump() for user_response in sample_user_responses]


def test_get_repos_empty(client):
    """
    Test the /api/repos endpoint when the database is empty.
    This test checks if the endpoint returns an empty list when there are no repositories in the database.
    """
    response = client.get("/api/repos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_repos_with_data(client, db_session, sample_users, sample_user_responses):
    """
    Test the /api/repos endpoint when the database contains repository data.
    This test checks if the endpoint returns the expected list of repositories when there are repositories in the database.
    """
    # Save sample users and their repositories to the database
    for user_stats, user_repos in sample_users:
        db_user = db.User(
            id=user_stats.id,
            username=user_stats.username,
            total_repos=user_stats.total_repos,
            total_stars=user_stats.total_stars,
            total_commits=user_stats.total_commits,
            average_stars_per_repo=user_stats.average_stars_per_repo,
            most_used_language=user_stats.most_used_language
        )
        db_session.add(db_user)
        db_session.flush()  # Flush to get the user ID for foreign key relationships

        # Save associated repositories
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
            db_session.add(db_repo)

    db_session.commit()

    # Now test the endpoint
    response = client.get("/api/repos")
    assert response.status_code == 200
    repos_data = response.json()
    expected_repos = []
    for user_response in sample_user_responses:
        expected_repos.extend([repo.model_dump() for repo in user_response.repos])
    assert len(repos_data) == len(expected_repos)
    assert repos_data == expected_repos

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

# Tests for the /api/analyze/{username} endpoint can be added here, 
# but they would require mocking the GitHub API responses and maybe the database interactions too, 
# which can be complex and is not included in this example.
# Same thing for the /api/users/{username} endpoint, as it would require mocking the GitHub API to fetch user ID
# and repositories.