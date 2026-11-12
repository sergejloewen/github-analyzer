import pytest
import responses
import requests
from src import process_data as pd
from src import exceptions as ex


# test file inlcudes tests for process_data.py but also for exceptions.py
# as they are closely related and exceptions are raised in process_data.py functions

# potentially add tests for pydantic models (validate input themselves already) and get_user_input function, 
# might not be critical for now but could be useful for ensuring input validation and
# letting the user continue and not throw exceptions in the main function, 
# but rather handle them gracefully and let the user continue to enter a valid username


@pytest.fixture
def raw_json_data():
    """
    Fixture providing valid raw data for testing analyze_repos function.
    """
    return [
        {
            "id": 12345678,
            "name": "python-data-analyzer",
            "full_name": "testuser/python-data-analyzer",
            "private": False,
            "html_url": "https://github.com/testuser/python-data-analyzer",
            "description": "Ein tolles Projekt zur Datenanalyse",
            "owner": {"login": "testuser", "id": 1},
            "stargazers_count": 12,
            "watchers_count": 12,
            "language": "Python",
            "forks_count": 2,
            "open_issues_count": 0,
            "created_at": "2026-01-15T08:00:00Z",
            "updated_at": "2026-10-18T10:30:00Z",
            "commits_url": "https://github.com{/sha}"
        },
        {
            "id": 87654321,
            "name": "my-portfolio-website",
            "full_name": "testuser/my-portfolio-website",
            "private": False,
            "html_url": "https://github.com/testuser/my-portfolio-website",
            "description": None,
            "owner": {"login": "testuser", "id": 1},
            "stargazers_count": 3,
            "watchers_count": 3,
            "language": "TypeScript",
            "forks_count": 0,
            "open_issues_count": 1,
            "created_at": "2026-05-20T14:22:00Z",
            "updated_at": "2026-09-01T12:00:00Z",
            "commits_url": "https://github.com{/sha}"
        },
        {
            "id": 12387543,
            "name": "smart-home-automation",
            "full_name": "testuser/smart-home-automation",
            "private": False,
            "html_url": "https://github.com/testuser/smart-home-automation",
            "description": None,
            "owner": {"login": "testuser", "id": 1},
            "stargazers_count": 3,
            "watchers_count": 3,
            "language": None,
            "forks_count": 0,
            "open_issues_count": 1,
            "created_at": "2026-05-20T14:22:00Z",
            "updated_at": "2026-09-01T12:00:00Z",
            "commits_url": "https://github.com{/sha}"
        }
    ]

@pytest.fixture
def filtered_user_repos():
    """
    Fixture providing valid user respositories for testing calculate_stats function.
    """
    return [
        pd.GitHubUserRepo(
            id=12345678,
            owner_id=1,
            owner_username="testuser",
            name="python-data-analyzer",
            stargazers_count=12,
            language="Python",
            description="Ein tolles Projekt zur Datenanalyse",
        ),
        pd.GitHubUserRepo(
            id=87654321,
            owner_id=1,
            owner_username="testuser",
            name="my-portfolio-website",
            stargazers_count=3,
            language="TypeScript",
            description="",
        ),
        pd.GitHubUserRepo(
            id=12387543,
            owner_id=1,
            owner_username="testuser",
            name="smart-home-automation",
            stargazers_count=3,
            language="Unknown",
            description="",
        )
    ]

@pytest.fixture
def user_id_name():
    """
    Fixture providing valid user id and username for testing calculate_stats function.
    """
    return 1, "testuser"

@responses.activate
def test_fetch_user_repos_valid_username(raw_json_data):
    """
    Test fetching repositories for a valid GitHub username.
    """

    responses.add(
        responses.GET,
        "https://api.github.com/users/octocat/repos",
        json=raw_json_data,
        status=200
    )

    username = "octocat" # valid GitHub username
    repos = pd.fetch_user_repos(username)
    assert isinstance(repos, list)
    assert all(isinstance(repo, dict) for repo in repos)
    assert len(repos) > 0 # Assuming octocat has public repositories
    assert len(repos) == 3 # Assuming octocat has 3 public repositories
    assert all('name' in repo for repo in repos) # Check if 'name' key exists in each repo dictionary

@responses.activate
def test_fetch_user_repos_invalid_username():
    """
    Test fetching repositories for an invalid GitHub username.
    Should raise GitHubUserNotFoundError.
    """

    invalid_username = "thisuserdoesnotexist1234567890"
    url = f"https://api.github.com/users/{invalid_username}/repos"

    # Mock the API response to simulate a 404 Not Found for an invalid username
    responses.add(responses.GET, url, status=404)

    with pytest.raises(ex.GitHubUserNotFoundError) as exc_info:
        pd.fetch_user_repos(invalid_username)
    assert exc_info.type == ex.GitHubUserNotFoundError

@responses.activate
def test_fetch_user_repos_empty_username():
    """
    Test fetching repositories for an empty GitHub username.
    Should raise GitHubUserNotFoundError.
    """

    empty_username = ""
    url = f"https://api.github.com/users/{empty_username}/repos"

    # Mock the API response to simulate a 404 Not Found for an empty username
    responses.add(responses.GET, url, status=404)
    
    with pytest.raises(ex.GitHubUserNotFoundError) as exc_info:
        pd.fetch_user_repos(empty_username)
    assert exc_info.type == ex.GitHubUserNotFoundError

@responses.activate
def test_fetch_user_repos_rate_limit():
    """
    Test fetching repositories when the rate limit is exceeded.
    Should raise a GitHubRateLimitError.
    """
    
    username = "octocat"
    url = f"https://api.github.com/users/{username}/repos"

    # Mock the API response to simulate rate limit exceeded
    responses.add(responses.GET, url, status=403)

    resp = requests.get(url)
    assert resp.status_code == 403

    with pytest.raises(ex.GitHubRateLimitError) as exc_info:
        pd.fetch_user_repos(username)
    assert exc_info.type == ex.GitHubRateLimitError

@responses.activate
def test_fetch_user_repos_too_many_requests():
    """
    Test fetching repositories when the rate limit is exceeded with 429 status code.
    Should raise a GitHubRateLimitError.
    """
    
    username = "octocat"
    url = f"https://api.github.com/users/{username}/repos"

    # Mock the API response to simulate rate limit exceeded
    responses.add(responses.GET, url, status=429)

    resp = requests.get(url)
    assert resp.status_code == 429

    with pytest.raises(ex.GitHubRateLimitError) as exc_info:
        pd.fetch_user_repos(username)
    assert exc_info.type == ex.GitHubRateLimitError

@responses.activate
def test_fetch_user_repos_GitHubAPI_error():
    """
    Test fetching repositories when a network error occurs.
    Should raise a GitHubNetworkError.
    """

    username = "octocat"
    url = f"https://api.github.com/users/{username}/repos"

    # Simulate a network error to simulate a server error status code 500
    responses.add(responses.GET, url, status=500)

    resp = requests.get(url)
    assert resp.status_code == 500

    with pytest.raises(ex.GitHubAPIError) as exc_info:
        pd.fetch_user_repos(username)  
    assert exc_info.type == ex.GitHubAPIError

@responses.activate
def test_fetch_user_repos_network_error():
    """
    Test fetching repositories when a network error occurs.
    Should raise a GitHubNetworkError.
    """

    username = "octocat"
    url = f"https://api.github.com/users/{username}/repos"

    # Simulate a network error
    responses.add(responses.GET, url, body=requests.exceptions.ConnectionError("Network error"))

    with pytest.raises(ex.GitHubNetworkError) as exc_info:
        pd.fetch_user_repos(username)
    assert exc_info.type == ex.GitHubNetworkError

def test_analyze_repos_with_empty_data():
    """
    Test analyzing repositories with empty raw data.
    Should return an empty list.
    """

    empty_raw_data = []
    result = pd.analyze_repos(empty_raw_data)
    assert result == []
    assert isinstance(result, list)
    assert len(result) == 0

def test_analyze_repos_with_valid_data(raw_json_data):
    """
    Test analyzing repositories with valid raw data.
    Should return a list of GitHubUserRepo instances.
    """

    result = pd.analyze_repos(raw_json_data)
    assert isinstance(result, list)
    assert all(isinstance(repo, pd.GitHubUserRepo) for repo in result)
    assert len(result) == len(raw_json_data)
    assert result[0].name == raw_json_data[0]["name"]
    assert result[0].stars == raw_json_data[0]["stargazers_count"]
    assert result[0].id == raw_json_data[0]["id"]
    assert result[1].name == raw_json_data[1]["name"]
    assert result[1].stars == raw_json_data[1]["stargazers_count"]
    assert result[1].id == raw_json_data[1]["id"]
    assert result[2].name == raw_json_data[2]["name"]
    assert result[2].stars == raw_json_data[2]["stargazers_count"]
    assert result[2].id == raw_json_data[2]["id"]

def test_calculate_stats_with_empty_repos():
    """
    Test calculating statistics with an empty list of user repositories.
    Should return UserStats with all values set to 0 or None.
    """

    empty_user_repos = []
    stats = pd.calculate_stats(empty_user_repos, None, None)
    assert isinstance(stats, pd.UserStats)
    assert stats.id == None
    assert stats.username == None
    assert stats.total_repos == 0
    assert stats.total_stars == 0
    assert stats.average_stars_per_repo == 0.0
    assert stats.most_used_language is 'Unknown'

def test_calculate_stats_with_valid_repos(filtered_user_repos, user_id_name):
    """
    Test calculating statistics with a valid list of user repositories.
    Should return UserStats with correct calculated values.
    """

    user_id, username = user_id_name
    stats = pd.calculate_stats(filtered_user_repos, user_id, username)
    

    assert isinstance(stats, pd.UserStats)
    assert stats.id == user_id
    assert stats.username == username
    assert stats.total_repos == len(filtered_user_repos)
    assert stats.total_stars == sum(repo.stars for repo in filtered_user_repos)
    assert stats.average_stars_per_repo == (stats.total_stars / stats.total_repos) if stats.total_repos > 0 else 0.0
    assert stats.most_used_language in [repo.language for repo in filtered_user_repos if repo.language != 'Unknown']

def test_visualize_repos_with_valid_data(filtered_user_repos, user_id_name):
    """
    Test visualizing repositories with valid user repositories.
    Should not raise any exceptions.
    """

    user_id, username = user_id_name
    stats = pd.calculate_stats(filtered_user_repos, user_id, username)
    pd.visualize_repos(filtered_user_repos, stats)  # Should not raise any exceptions

    assert True  # If no exceptions are raised, the test passes

def test_visualize_repos_with_empty_data(capsys):
    """
    Test visualizing repositories with empty user repositories.
    Should not raise any exceptions.
    """

    empty_user_repos = []
    stats = pd.calculate_stats(empty_user_repos, None, None)
    pd.visualize_repos(empty_user_repos, stats)  # Should not raise any exceptions
    captured = capsys.readouterr()

    assert True  # If no exceptions are raised, the test passes
    assert captured.out == "No public repositories to visualize.\n"  # Check if the correct message is printed