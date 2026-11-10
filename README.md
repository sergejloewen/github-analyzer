# Github Analyzer

Github Analyzer is a Tool to collect, analyze and visualize GitHub Users repository data,
which will be stored in a database and serve the future API and web dashboard.

## Purpose of this App

It should serve as a quick and easy way to get basic data about a user's repositories
in a simple visual manner.

## Architecture

WIP

## Tech Stack

- Python
- FastAPI (WIP)
- Pydantic
- SQLAlchemy
- PostgreSQL (WIP) / zunächst SQLite
- pytest
- Docker (WIP)
- GitHub Actions (WIP)

## Setup

Clone the repository, go into the folder and use the following command in terminal to set up
the project environment using uv.

On Windows:

```text
uv run main.py
```

## Tests

Pytest is used for testing the app and in the test_process_data.py file there are all the tests written
for both process_data.py and exceptions.py, as they are closely related.
TODO: Write tests for the database operations

## Screenshots/ GIFs

WIP

## Known Limitations

WIP

## Future Plans

- Upgrading Database to PostgresSQL
- Web Dashboard
- Docker and Docker image for easy Setup
- GitHub Actions for automatic Build Testing
