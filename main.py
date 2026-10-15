import requests;

def main(username):
    githubAPI = requests.get("https://api.github.com")
    print(githubAPI.status_code)

    #tensorflowRepo = requests.get("https://api.github.com/repos/tensorflow/tensorflow")
    #print(tensorflowRepo.status_code)

    exampleUser = requests.get(f"https://api.github.com/users/{username}")
    print(exampleUser.status_code)

    exampleUserRepos = requests.get(f"https://api.github.com/users/{username}/repos")
    print(exampleUserRepos.status_code)

    for x, y in exampleUser.json().items():
        print(f"{x}: {y}")

    for x in exampleUserRepos.json():
        print(f"Repo: {x['name']}")
        print(f"Description: {x['description']}")
        print(f"URL: {x['html_url']}")
        print(f"Language: {x['language']}")
        print(f"Forks: {x['forks_count']}")
        print(f"Stars: {x['stargazers_count']}")
        print(f"Watchers: {x['watchers_count']}")
        print(f"Open Issues: {x['open_issues_count']}")
        print("")
    
    #print("Repo: " + exampleUserRepos.json()[0]['name'])


if __name__ == "__main__":
    #TODO refactor into different class & functions
    username = input("Enter a GitHub username: ")
    main(username)