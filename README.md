# Github Analyzer

Github Analyzer is a tool consisting of a backend API, web dashboard and database
to collect, analyze and visualize GitHub Users repository data.

## Purpose of this App

It should serve as a quick and easy way to get basic data about a user's repositories
in a simple visual manner.

## Architecture

The app is a 3-tier architecture consisting of the PostgreSQL,
FastAPI-Backend and an interactive Streamlit-Frontend.

UML diagram to be added (WIP)

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- pytest
- Streamlit
- Docker
- GitHub Actions

## Setup

The app is fully dockerized, so clone the repository and follow the following steps
The only requirement is having a running docker desktop.

**Configure Environment Variables**
Create a file named `.env` in the root directory and choose your access credentials for the PostgreSQL database:

```text
POSTGRES_USER=choose_a_username
POSTGRES_PASSWORD=choose_a_safe_password
POSTGRES_DB=github_analyzer
```

*(Hint: The `.env`-file is added to `.gitignore` and therefore will not be uploaded to GitHub due to security reasons.)*

**Start the App:**
Boot up the entire multi-container-network (Database, API and Dashboard) with one command:

```bash
docker compose up --build
```

**Open in Browser:**
Once all containers successfully booted up, you can access each service over the following URLs:

- 📊 **Streamlit Web-Dashboard:** [http://localhost:8501](http://localhost:8501)
- 🌐 **FastAPI API-Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Stop the App

To properly shutdown the whole container-network, press `Ctrl + C` in the terminal or use following command
while being in the root directory:

```bash
docker compose down
```

## Tests

Pytest is used for testing the app and in the test_process_data.py file there are all the tests written
for both process_data.py and exceptions.py, as they are closely related.

TODO: Write tests for the database operations, backend and frontend

## Screenshots/ GIFs

WIP

## Known Limitations

- Currently when the backend interacts with the GitHub API it is affected by pagination and
therefore only shows 30 results if there are more than 30 items (repos for instance),
only exception is number of commits per repo as those are already changed to account for that
- total_commits in for each users might be inflated in the case of repos being worked on by multiple people
and the commits getting counted towards the repo owner

## Future Plans

All planned features are implemented as of now. The development for now is finished.
(potentially provide a pre-built docker image for the easiest setup)
