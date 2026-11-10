# Github Analyzer

Github Analyzer is a tool consisting of a backend API, web dashboard and database
to collect, analyze and visualize GitHub Users repository data.

## Purpose of this App

It should serve as a quick and easy way to get basic data about a user's repositories
in a simple visual manner.

## Architecture

The app is a 3-tier architecture consisting of the database (SQlite/SQLAlchemy as of right now),
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
- GitHub Actions (WIP)

## Setup

Clone the repository, go into the folder and use the following command in terminal to set up
the project environment using uv.

(WIP) Change to accomodate Docker

On Windows:

```text
uv run main.py
```

## Tests

Pytest is used for testing the app and in the test_process_data.py file there are all the tests written
for both process_data.py and exceptions.py, as they are closely related.
TODO: Write tests for the database operations, backend and frontend

## Screenshots/ GIFs

WIP

## Known Limitations

WIP

## Future Plans

- provide Docker image for easy Setup
- GitHub Actions for automatic Build Testing
