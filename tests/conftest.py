import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db
from src.schemas import UserResponse, RepoResponse
from src.process_data import GitHubUserRepo, UserStats

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:meingeheimnis@localhost:5432/github_analyzer_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, join_transaction_mode="create_savepoint")

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Set up the test database before running tests and tear it down afterward.
    """
    # Create the test database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the test database tables after tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Create a new database session for a test and roll back any changes after the test is done.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a TestClient for the FastAPI app with a dependency override for the database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_users():
    """
    Fixture to provide sample user data for testing.
    Returns a list of UserStats and corresponding GitHubUserRepo instances.
    """
    user1_stats = UserStats(
        id=1,
        username="testuser1",
        total_repos=2,
        total_stars=10,
        average_stars_per_repo=5.0,
        most_used_language="Python"
    )
    user1_repos = [
        GitHubUserRepo(id=101, owner_id=1, name="repo1", language="Python", stargazers_count=5, description="Test repo 1"),
        GitHubUserRepo(id=102, owner_id=1, name="repo2", language="JavaScript", stargazers_count=5, description="Test repo 2")
    ]

    user2_stats = UserStats(
        id=2,
        username="testuser2",
        total_repos=1,
        total_stars=3,
        average_stars_per_repo=3.0,
        most_used_language="Java"
    )
    user2_repos = [
        GitHubUserRepo(id=201, owner_id=2, name="repoA", language="Java", stargazers_count=3, description="Test repo A")
    ]

    user3_stats = UserStats(
        id=3,
        username="testuser3",
        total_repos=0,
        total_stars=0,
        average_stars_per_repo=0.0,
        most_used_language=""
    )
    user3_repos = []

    user4_stats = UserStats(
        id=4,
        username="testuser4",
        total_repos=4,
        total_stars=20,
        average_stars_per_repo=5.0,
        most_used_language="Python"
    )
    user4_repos = [
        GitHubUserRepo(id=401, owner_id=4, name="repoD", language="Python", stargazers_count=5, description="Test repo D"),
        GitHubUserRepo(id=402, owner_id=4, name="repoE", language="Python", stargazers_count=5, description="Test repo E"),
        GitHubUserRepo(id=403, owner_id=4, name="repoF", language="Python", stargazers_count=5, description="Test repo F"),
        GitHubUserRepo(id=404, owner_id=4, name="repoG", language="Python", stargazers_count=5, description="Test repo G")
    ]

    return [
        (user1_stats, user1_repos),
        (user2_stats, user2_repos),
        (user3_stats, user3_repos),
        (user4_stats, user4_repos)
    ]

@pytest.fixture
def sample_user_responses():
    """
    Fixture to provide sample response data for testing.
    Returns a list of UserResponse and corresponding RepoResponse instances.
    """
    user1_response = UserResponse(
        id=1,
        username="testuser1",
        repos=[
            RepoResponse(id=101, owner_id=1, name="repo1", language="Python", stars=5, description="Test repo 1"),
            RepoResponse(id=102, owner_id=1, name="repo2", language="JavaScript", stars=5, description="Test repo 2")
        ],
        total_repos=2,
        total_stars=10,
        average_stars_per_repo=5.0,
        most_used_language="Python"
    )

    user2_response = UserResponse(
        id=2,
        username="testuser2",
        repos=[
            RepoResponse(id=201, owner_id=2, name="repoA", language="Java", stars=3, description="Test repo A")
        ],
        total_repos=1,
        total_stars=3,
        average_stars_per_repo=3.0,
        most_used_language="Java"
    )

    user3_response = UserResponse(
        id=3,
        username="testuser3",
        repos=[],
        total_repos=0,
        total_stars=0,
        average_stars_per_repo=0.0,
        most_used_language=""
    )

    user4_response = UserResponse(
        id=4,
        username="testuser4",
        repos=[
            RepoResponse(id=401, owner_id=4, name="repoD", language="Python", stars=5, description="Test repo D"),
            RepoResponse(id=402, owner_id=4, name="repoE", language="Python", stars=5, description="Test repo E"),
            RepoResponse(id=403, owner_id=4, name="repoF", language="Python", stars=5, description="Test repo F"),
            RepoResponse(id=404, owner_id=4, name="repoG", language="Python", stars=5, description="Test repo G")
        ],
        total_repos=4,
        total_stars=20,
        average_stars_per_repo=5.0,
        most_used_language="Python"
    )

    return [user1_response, user2_response, user3_response, user4_response]