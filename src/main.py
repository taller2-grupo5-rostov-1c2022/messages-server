from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from requests.auth import HTTPBasicAuth
import os

from src.app import messages, users

API_VERSION_PREFIX = "/api/v1"

API_KEY = os.environ.get("API_KEY") or "key"
API_KEY_NAME = "api_key"

auth = HTTPBasicAuth(API_KEY_NAME, API_KEY)
headers = {"Accept": "application/json", API_KEY_NAME: API_KEY}


async def get_api_key(
    api_key_header: str = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=True)),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403)


app = FastAPI(
    title="Messages API",
    description="Spotifiuby's API to send and receive messages",
    version="0.0.1",
    dependencies=[Depends(get_api_key)],
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def healthcheck():
    """Endpoint Healthcheck"""
    return "ok"


app.include_router(users.router, prefix=API_VERSION_PREFIX)
app.include_router(messages.router, prefix=API_VERSION_PREFIX)
