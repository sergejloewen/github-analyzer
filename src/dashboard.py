import streamlit as st
import requests
import pandas as pd

repos_url = "http://127.0.0.1:8000/api/repos"
users_url = "http://127.0.0.1:8000/api/users"

st.title("GitHub Analyzer Dashboard")

col1, col2, col3 = st.columns([0.15, 0.2, 0.6])

with col1:
    st.button("Show Users", key="show_users_button")
with col2:
    st.button("Show Repositories", key="show_repos_button")
with col3:
    st.button("Clear Output", key="clear_output_button")


username = st.text_input("Enter GitHub username:", key="username_input")
url = f"http://127.0.0.1:8000/api/analyze/{username}"

col_left, col_right = st.columns([0.85, 0.15])

with col_left:
    st.button("Analyze", key="analyze_button")
with col_right:
    st.button("Clear", key="clear_button", type="primary", on_click=lambda: st.session_state.update({"username_input": ""}))

if st.session_state.get("analyze_button"):
    if username:
        try:
            response = requests.post(url)
            if response.status_code == 200:
                user_data = response.json()
                # Display user data and statistics without repositories
                st.write(f"### User Data and Statistics for {user_data['username']}")
                df_user = pd.DataFrame([{'id': user_data['id'],
                                         'username': user_data['username'],
                                         'Total Repos': user_data['total_repos'],
                                         'Total Stars': user_data['total_stars'],
                                         'Total Commits': user_data['total_commits'],
                                         'Average Stars per Repo': user_data['average_stars_per_repo'],
                                         'Most Used Language': user_data['most_used_language']}])
                st.dataframe(df_user)

                # Repositories of the user
                df_repos = pd.DataFrame(user_data['repos'])
                if not df_repos.empty:
                    st.write(f"### Repositories for {user_data['username']}")
                    st.dataframe(df_repos[['name', 'language', 'stars', 'commits']])
                    st.write("### Language Distribution")
                    # Goes through the 'language' column and counts the occurrences of each language
                    language_counts = df_repos['language'].value_counts()
                    st.bar_chart(language_counts, horizontal=True)
                else:
                    st.write(f"No public repositories found for user {user_data['username']}.")

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred - User not found: {e}")
    
if st.session_state.get("show_users_button"):
    try:
        response = requests.get(users_url)
        if response.status_code == 200:
            users_data = response.json()

            # Remove all metadata fields from user repos besides the name field
            for user in users_data:
                # Check if the user has a "repos" field and if it's a list
                if "repos" in user and isinstance(user["repos"], list):
                    # Extract only the "name" field from each repository and join them into a single string
                    repo_names = [repo["name"] for repo in user["repos"]]
                    user["repos"] = ",  ".join(repo_names)

            st.write("All Users in the Database:")
            df = pd.DataFrame(users_data)
            st.dataframe(df)

            st.write("### Most Used Language Distribution Across All Users")
            # Counts the occurrences of each language in the 'most_used_language' column and creates a bar chart
            language_counts = df['most_used_language'].value_counts()
            st.bar_chart(language_counts, horizontal=True)

    except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while fetching users: {e}")

if st.session_state.get("show_repos_button"):
    try:
        response = requests.get(repos_url)
        if response.status_code == 200:
            repos_data = response.json()
            df = pd.DataFrame(repos_data)
            st.write("All Repositories in the Database:")
            st.dataframe(df)

            st.write("### Most Used Language Distribution Across All Repositories")
            # Counts the occurrences of each language in the 'language' column of a repo
            language_counts = df['language'].value_counts()
            st.bar_chart(language_counts, horizontal=True)

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching repositories: {e}")

if st.session_state.get("clear_output_button"):
    pass  # The output will be cleared automatically when the button is clicked, as Streamlit reruns the script.
