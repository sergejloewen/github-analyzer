import os
import re
from pydantic import BaseModel, Field
import requests
from src import exceptions as ex
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class GitHubUserRepo(BaseModel):
    """
    Data model representing a GitHub repository with relevant fields.
    """

    id: int | None = None
    owner_id: int | None = None
    owner_username: str | None = None
    name: str
    stars: int = Field(alias='stargazers_count')
    language: str | None = 'Unknown'
    description: str | None = None

class UserStats(BaseModel):
    """
    Data model representing statistics about a user's GitHub repositories.
    """

    id: int | None = None
    username: str | None = None
    total_repos: int
    total_stars: int
    average_stars_per_repo: float
    most_used_language: str | None = None

def get_user_input() -> str:
    """
    Prompt the user to enter a GitHub username.
    """
    #input validation not needed as function isn't used anymore
    return input("Enter a GitHub username: ")

def safe_get(url: str, params: dict | None = None, headers: dict | None = None) -> requests.Response:
    """
    Perform a GET request to the specified URL and handle potential exceptions.
    """
    headers = {"Accept": "application/vnd.github+json"}

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, timeout=5, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            raise ex.GitHubUserNotFoundError(f"GitHub user not found or does not exist. (HTTP Status code: {response.status_code})") from err
        elif response.status_code in [403, 429]:
            raise ex.GitHubRateLimitError(f"GitHub API rate limit exceeded. (HTTP Status code: {response.status_code})") from err
        else:
            raise ex.GitHubAPIError(f"GitHub API returned an error. (HTTP Status code: {response.status_code})") from err
    except requests.exceptions.ConnectionError as err:
        raise ex.GitHubNetworkError("Network error occurred while trying to access the GitHub API.") from err

def fetch_user_repos(username: str) -> list[dict]:
    """
    Fetch the user's repositories from the GitHub API
    Using Query Parameter 'per_page=100' to get all repositories.
    The GitHub API returns a maximum of 100 repositories per page.
    """

    page = 1
    all_repos = []
    url = f"https://api.github.com/users/{username}/repos"

    while True:
        params = {"per_page": 100, "page": page}    # Query parameters to fetch 100 repositories per page
        response = safe_get(url, params=params)
        repos = response.json()

        # If the response is empty or None, it means there are no more repositories to fetch, there was an error
        # or the user has no public repositories, so we break the loop
        if not repos:
            break

        all_repos.extend(repos)

        if len(repos) < 100:
            break  # No more pages to fetch

        page += 1

    return all_repos

def fetch_user_id(username: str) -> int:
    """
    Fetch the user's ID from the GitHub API
    """
    url = f"https://api.github.com/users/{username}"
    response = safe_get(url)
    user_data = response.json()
    return user_data.get("id", None)

def analyze_repos(raw_data: list[dict]) -> list[GitHubUserRepo]:
    """
    Filter raw data and create GitHubUserRepo instances
    """

    user_repos = []

    # check if list is empty or none
    if not raw_data:
        print("No public repositories found for this user.")
        return []
    
    # Create GitHubUserRepo instances from the raw data, filtering it in the process and append them to the list
    for repo_data in raw_data:
        repo = GitHubUserRepo(**repo_data)

        # Handle cases where Language is None
        if repo.language is None:
            repo.language = 'Unknown'

        # Adds owner_username and owner_id to the GitHubUserRepo instance
        # As the GitHub API returns the owner information in a nested dictionary, 
        # we need to extract it and assign it to the respective fields in the GitHubUserRepo instance.    
        if repo.owner_username is None:
            repo.owner_username = repo_data.get('owner', {}).get('login', None)

        if repo.owner_id is None:
            repo.owner_id = repo_data.get('owner', {}).get('id', None)

        user_repos.append(repo) # think about using yield if necessary

    return user_repos

def calculate_stats(user_repos: list[GitHubUserRepo], user_id: int, username: str) -> UserStats:
    """
    calculate statistics based on the user's repositories
    """

    id = user_id
    username = username
    total_repos = len(user_repos)
    total_stars = sum(repo.stars for repo in user_repos)
    total_languages = {}

    # calculate average stars per repo, handle division by zero
    if total_repos > 0:
        average_stars_per_repo = total_stars / total_repos
    else:
        average_stars_per_repo = 0.0
        
    # calculate all languages used in the repositories and their counts
    for repo in user_repos:
        if not total_languages.get(repo.language):
            total_languages[repo.language] = 1
        else:
            total_languages[repo.language] += 1

    # remove 'Unknown' from the language count if it exists
    if 'Unknown' in total_languages:
        del total_languages['Unknown']

    # find the most used language in the list of repositories if the list is not empty,
    # Unknown and None are filtered out already
    if not total_languages:
        most_used_language = 'Unknown'
    else:
        most_used_language = max(total_languages, key=total_languages.get)

    return UserStats(
        id=id,
        username=username,
        total_repos=total_repos,
        total_stars=total_stars,
        average_stars_per_repo=average_stars_per_repo,
        most_used_language=most_used_language
    )

# Not being used anymore as the visualization is now being done in the web dashboard
def visualize_repos(user_repos: list[GitHubUserRepo], stats: UserStats) -> None:
    """
    Visualize the user's repositories and statistics in a simple table format in CLI
    """

    # Check if there are any repositories to visualize
    if not user_repos:
        print("No public repositories to visualize.")
        return
    
    # Print the table for user repositories and their statistics
    print(f"\n{'Repository':<30} {'Stars':<10} {'Language':<15}")
    print("-" * 70)
    for repo in user_repos:
        print(f"{repo.name:<30} {repo.stars:<10} {repo.language:<15}")

    print("\nStatistics:")
    print(f"Total Repositories: {stats.total_repos}")
    print(f"Total Stars: {stats.total_stars}")
    print(f"Average Stars per Repository: {stats.average_stars_per_repo:.2f}")
    print(f"Most Used Language: {stats.most_used_language}")