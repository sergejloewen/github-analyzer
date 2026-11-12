# Github Analyzer

[![GitHub Analyzer CI Pipeline](https://github.com/sergejloewen/github-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/sergejloewen/github-analyzer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=fff)](#)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](#)

GitHub Analyzer is a full-stack web application consisting of a backend API, an interactive web dashboard, and a relational database to collect, analyze, and visualize GitHub user repository data.

## Purpose of this App

This project provides a quick and acessible way to inspect and visualize key metrics of a GitHub user's repositories
in one place.

## Screenshots/ GIFs

![GitHub Analyzer Demo](assets/demo.gif)

## Architecture

The application follows a **3-tier architecture**:

1. **Frontend:** Interactive dashboard built with **Streamlit**
2. **Backend:** REST API built with **FastAPI** and **SQLAlchemy**
3. **Database:** Persistent storage using **PostgreSQL**

```mermaid
flowchart LR
    User([👤 User]) <--> UI[Streamlit Dashboard<br/>:8501]
    UI <-->|REST / JSON| API[FastAPI Backend<br/>:8000]
    API <-->|SQLAlchemy| DB[(PostgreSQL<br/>:5432)]
    API <-->|HTTPS| GH[GitHub REST API]
```

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, uv
- **Frontend:** Streamlit
- **Database:** PostgreSQL 16
- **Testing & CI:** Pytest, GitHub Actions
- **Deployment:** Docker, Docker Compose

## Setup

The application is fully dockerized. The only prerequisite is a running **Docker Desktop** (or Docker Engine) installation.

### 1. Configure Environment Variables

Create a file named `.env` in the root directory and configure your credentials:

```text
POSTGRES_USER=choose_a_username
POSTGRES_PASSWORD=choose_a_safe_password
POSTGRES_DB=github_analyzer

# Optional, but highly recommended to avoid GitHub API rate limits:
GITHUB_TOKEN=your_personal_github_token

# Optional overrides (only needed for custom local setups):
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/github_analyzer
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/github_analyzer_test
```

*(Note: Without a `GITHUB_TOKEN`, the GitHub API enforces a strict rate limit of 60 requests per hour, which can block requests when analyzing users with many repositories.)*
*(Note: The `.env`-file is included in `.gitignore` and will not be committed to version control.)*

### 2. Start the Application

Build and start the multi-container setup (Database, API and Dashboard) with a single command:

```bash
docker compose up --build
```

### 4. Open in Browser

Once all containers are running, open the following URLS in your browser:

- 📊 **Streamlit Web-Dashboard:** [http://localhost:8501](http://localhost:8501)
- 🌐 **FastAPI API-Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop the App

press `Ctrl + C` in the terminal or run:

```bash
docker compose down
```

## Running Tests

Unit and integration tests are implemented with **Pytest** (located in the `tests/` directory) and run automatically on every push via **GitHub Actions**.

to run the test suite locally using `uv`:

1. Start only the database container:

    ```bash
    docker compose up -d db
    ```

2. Create a test database inside the running container:

    ```bash
    docker exec github_postgres sh -c 'psql -U "\(POSTGRES_USER" -d "\)POSTGRES_DB" -c "CREATE DATABASE \"\${POSTGRES_DB}_test\";"'
    ```

3. Run Pytest:

    ```bash
    uv run pytest
    ```

## Design Decisions

- **Pagination Handling (`per_page=100`):** To fetch complete repository lists without excessive network overhead, the backend uses GitHub's maximum page size (`per_page=100`) and iterates through pages dynamically until all repositories are retrieved.
- **Avoiding N+1 API Requests (Excluding Commit Counts):** Initially, commit counts were fetched per repository. Because the GitHub REST API requires a separate request for each repository's commits, this caused an N+1 request pattern, severely increasing response times and exhausting unauthenticated rate limits (60 requests/hour). Removing per-repo commit queries keeps user lookups fast (typically 1–2 API calls per user) while still capturing key metrics like stars, languages, and repository counts.
