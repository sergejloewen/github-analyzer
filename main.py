from collections import Counter

import requests
from pydantic import BaseModel, Field

# Datenmodell für ein GitHub-Repository
class GitHubUserRepo(BaseModel):
    name: str
    stars: int = Field(alias='stargazers_count')
    language: str | None = 'Unknown'
    commits: int | None = 0     # currently not working
    description: str | None = None

class UserStats(BaseModel):
    total_repos: int
    total_stars: int
    total_commits: int
    average_stars_per_repo: float
    most_used_language: str | None = None

# Get the username from the user
def get_user_input() -> str:
    return input("Enter a GitHub username: ")

# Fetch the user's repositories from the GitHub API
def fetch_user_repos(username: str) -> list[dict]:
    #TODO fetch the number of commits for each repository made by the user
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

# Filter data and create GitHubUserRepo instances
def analyze_repos(raw_data: list[dict]) -> list[GitHubUserRepo]:
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
# calculate statistics based on the user's repositories
def calculate_stats(user_repos: list[GitHubUserRepo]) -> UserStats:
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

    del total_languages['Unknown']  # Remove 'Unknown' from the language count

    # find the most used language in the list of repositories, Unknown and None are filtered out already
    most_used_language = max(total_languages, key=total_languages.get)

    return UserStats(
        total_repos=total_repos,
        total_stars=total_stars,
        total_commits=total_commits,
        average_stars_per_repo=average_stars_per_repo,
        most_used_language=most_used_language
    )

# Visualize the user's repositories and statistics in a simple table format in CLI
def visualize_repos(user_repos: list[GitHubUserRepo], stats: UserStats) -> None:
    if not user_repos:
        print("No public repositories to visualize.")
        return
    
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

def main():
    # checking if the Github API is reachable
    githubAPI = requests.get("https://api.github.com")
    print(githubAPI.status_code)

    username = get_user_input()
    raw_data = fetch_user_repos(username)
    user_repos = analyze_repos(raw_data)
    stats = calculate_stats(user_repos)
    visualize_repos(user_repos, stats)


if __name__ == "__main__":
    main()