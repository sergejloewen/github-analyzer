import requests
import process_data as pd
import database as db
import interact_db as iDB

def main():
    # checking if the Github API is reachable
    githubAPI = requests.get("https://api.github.com")
    print(githubAPI.status_code)

    username = pd.get_user_input()
    user_id = pd.fetch_user_id(username)
    raw_data = pd.fetch_user_repos(username)
    user_repos = pd.analyze_repos(raw_data)
    stats = pd.calculate_stats(user_repos, user_id, username)
    # pd.visualize_repos(user_repos, stats)

    # Save the user, their statistics and repositories to the database
    with db.SessionLocal() as session:
        iDB.save_user_profile(session, stats, user_repos)

if __name__ == "__main__":
    main()