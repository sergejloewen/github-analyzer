from pydantic import BaseModel, Field
import requests
import exceptions as ex

# potentially add validation and testing for the models
class GitHubUserRepo(BaseModel):
    """
    Data model representing a GitHub repository with relevant fields.
    """

    name: str
    stars: int = Field(alias='stargazers_count')
    language: str | None = 'Unknown'
    commits: int | None = 0     # currently not working
    description: str | None = None

class UserStats(BaseModel):
    """
    Data model representing statistics about a user's GitHub repositories.
    """

    total_repos: int
    total_stars: int
    total_commits: int
    average_stars_per_repo: float
    most_used_language: str | None = None

def get_user_input() -> str:
    """
    Prompt the user to enter a GitHub username.
    """
    #TODO: Add input validation to ensure the username is valid 
    # and within length limits (e.g., no special characters, not empty, etc.)
    return input("Enter a GitHub username: ")

def safe_get(url: str) -> requests.Response:
    """
    Perform a GET request to the specified URL and handle potential exceptions.
    """

    try:
        response = requests.get(url, timeout=5)
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
    """
    #TODO fetch the number of commits for each repository made by the user, 
    # might require changing another method as the data might be already in the raw_data, but is not being used and calculated in the GitHubUserRepo Class

    url = f"https://api.github.com/users/{username}/repos"
    response = safe_get(url)
    return response.json()

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

        user_repos.append(repo) # think about using yield if necessary

    return user_repos

def calculate_stats(user_repos: list[GitHubUserRepo]) -> UserStats:
    """
    calculate statistics based on the user's repositories
    """

    total_repos = len(user_repos)
    total_stars = sum(repo.stars for repo in user_repos)
    total_commits = sum(repo.commits for repo in user_repos)
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
        total_repos=total_repos,
        total_stars=total_stars,
        total_commits=total_commits,
        average_stars_per_repo=average_stars_per_repo,
        most_used_language=most_used_language
    )

def visualize_repos(user_repos: list[GitHubUserRepo], stats: UserStats) -> None:
    """
    Visualize the user's repositories and statistics in a simple table format in CLI
    """

    # Check if there are any repositories to visualize
    if not user_repos:
        print("No public repositories to visualize.")
        return
    
    # Print the table for user repositories and their statistics
    print(f"\n{'Repository':<30} {'Commits':<10} {'Stars':<10} {'Language':<15}")
    print("-" * 70)
    for repo in user_repos:
        print(f"{repo.name:<30} {repo.commits:<10} {repo.stars:<10} {repo.language:<15}")

    print("\nStatistics:")
    print(f"Total Repositories: {stats.total_repos}")
    print(f"Total Stars: {stats.total_stars}")
    print(f"Total Commits: {stats.total_commits}")
    print(f"Average Stars per Repository: {stats.average_stars_per_repo:.2f}")
    print(f"Most Used Language: {stats.most_used_language}")