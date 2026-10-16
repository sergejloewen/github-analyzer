import requests
from pydantic import BaseModel, Field

# Datenmodell für ein GitHub-Repository
class GitHubUserRepo(BaseModel):
    name: str
    stars: int = Field(alias='stargazers_count')
    language: str | None = 'Unknown'
    commits: int | None = 0
    description: str | None = None

# Get the username from the user
def get_user_input() -> str:
    return input("Enter a GitHub username: ")

# Fetch the user's repositories from the GitHub API
def fetch_user_repos(username: str) -> list[dict]:
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
    
    # Create GitHubUserRepo instances from the raw data and append them to the list
    for repo_data in raw_data:
        repo = GitHubUserRepo(**repo_data)

        # Handle cases where Language is None
        if repo.language is None:
            repo.language = 'Unknown'

        user_repos.append(repo) # think about using yield if necessary

    return user_repos

def visualize_repos(user_repos: list[GitHubUserRepo]) -> None:
    if not user_repos:
        print("No public repositories to visualize.")
        return
    
    print(f"\n{'Repository':<30} {'Commits':<10} {'Stars':<10} {'Language':<15}")
    print("-" * 70)
    for repo in user_repos:
        print(f"{repo.name:<30} {repo.commits:<10} {repo.stars:<10} {repo.language:<15}")

def main():
    # checking if the Github API is reachable
    githubAPI = requests.get("https://api.github.com")
    print(githubAPI.status_code)

    username = get_user_input()
    raw_data = fetch_user_repos(username)
    user_repos = analyze_repos(raw_data)
    visualize_repos(user_repos)

if __name__ == "__main__":
    main()