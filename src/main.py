import requests
import process_data as pd

def main():
    # checking if the Github API is reachable
    githubAPI = requests.get("https://api.github.com")
    print(githubAPI.status_code)

    username = pd.get_user_input()
    raw_data = pd.fetch_user_repos(username)
    user_repos = pd.analyze_repos(raw_data)
    stats = pd.calculate_stats(user_repos)
    pd.visualize_repos(user_repos, stats)


if __name__ == "__main__":
    main()