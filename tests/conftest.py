import time

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app, API_VERSION_PREFIX
from src.postgres.database import get_db, Base
import requests_mock
import requests

import os

from src.repositories.message_utils import NOTIFICATIONS_ENDPOINT

SQLALCHEMY_DATABASE_URL = os.environ.get("TEST_POSTGRES_URL")


def api_matcher(request):
    if API_VERSION_PREFIX not in request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attepmted to call non-api endpoint",
        )
    return None


@pytest.fixture
def custom_requests_mock():
    m = requests_mock.Mocker(real_http=True)
    m.start()
    m.add_matcher(api_matcher)
    m.post(NOTIFICATIONS_ENDPOINT, status_code=status.HTTP_200_OK)

    try:
        yield m
    finally:
        m.stop()


@pytest.fixture(scope="session")
def connect_to_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    for x in range(10):
        try:
            print("Trying to connect to DB - " + str(x))
            engine.connect()
            break
        except Exception:  # noqa: E722 # Want to catch all exceptions
            time.sleep(1)
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
    yield engine


@pytest.fixture()
def session(connect_to_database):

    Base.metadata.drop_all(bind=connect_to_database)
    Base.metadata.create_all(bind=connect_to_database)
    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=connect_to_database
    )

    db = testing_session_local()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):

    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
