import asyncio
import time
import os

os.environ["TESTING"] = "1"
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app, API_VERSION_PREFIX
from src.mongo.database import get_db, db
import requests_mock


from src.repositories.message_utils import NOTIFICATIONS_ENDPOINT


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


@pytest.fixture(autouse=True)
async def client():
    try:
        yield TestClient(app)
    finally:
        print("DROPPING DATABASE")
        # db = asyncio.run(get_db())
        collections = await db.list_collection_names()
        for collection in collections:
            await db.drop_collection(collection)
