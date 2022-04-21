from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.cors import CORSMiddleware
from src.classes import UserUpdate, User
import requests
from requests.auth import HTTPBasicAuth
import os


if os.environ.get("TESTING") == "1":
    print("RUNNING IN TESTING MODE: MOCKING ACTIVATED")
    from src.mocks.firebase.database import db
    from src.mocks.firebase.bucket import bucket
else:
    from src.firebase.access import db, bucket

app = FastAPI()

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


@app.get("/api/v1/users/")
def get_all_users(_api_key: APIKey = Depends(get_api_key)):
    """Returns all users"""
    users = db.collection("users").stream()
    users_dict = {}
    for user in users:
        users_dict[user.id] = user.to_dict()
    return users_dict


@app.get("/api/v1/users/{user_name}")
def get_user_by_id(user_name: str, _api_key: APIKey = Depends(get_api_key)):
    """Returns a user by its id or 404 if not found"""
    db_entry = db.collection("users").document(user_name).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="user not found")

    return db_entry.to_dict()


@app.post("/api/v1/users/")
def post_user(user_name: str, _api_key: APIKey = Depends(get_api_key)):
    """Creates a user and returns its username"""
    ref = db.collection("users").document(user_name)
    ref.set(User(songs=[], playlists=[]).dict())

    return {"id": ref.id}


@app.delete("/api/v1/users/")
def delete_user(user_name: str, _api_key: APIKey = Depends(get_api_key)):
    """Deletes a user given its username or 404 if not found"""
    try:
        db.collection("users").document(user_name).delete()
        blob = bucket.blob(user_name)
        blob.delete()
    # TODO: catchear solo NotFound
    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404, detail="User not found"
        ) from entry_not_found
    return user_name


@app.put("/api/v1/users/")
def update_user(
    user_name: str, user_update: UserUpdate, _api_key: APIKey = Depends(get_api_key)
):
    """Updates user and returns its username or 404 if not found"""
    db.collection("users").document(user_name).update(
        user_update.info.dict(exclude_unset=True)
    )

    return user_name


@app.post("/api/v1/new_song/{song_id}")
def new_song(song_id: str, user_name: str, _api_key: APIKey = Depends(get_api_key)):
    """Adds a song to the user's list of published songs and returns its username"""
    db_entry = db.collection("users").document(user_name).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="User not found")

    user = db_entry.to_dict()
    user["songs"].append(song_id)
    db.collection("users").document(user_name).update(user)
    return user_name


@app.delete("/api/v1/delete_song/{song_id}")
def delete_song(user_name: str, song_id: str, _api_key: APIKey = Depends(get_api_key)):
    """Deletes a song if the user is authorized.
    Returns the id of the song, 401 if not authorized, or 404 if the user or the song was not found"""

    r = requests.get(
        "https://rostov-song-server.herokuapp.com/api/v1/songs/" + song_id,
        headers=headers,
    )
    song = r.json()

    artist_name = song["artist_name"]
    if artist_name != user_name:
        raise HTTPException(status_code=401, detail="User not authorized")

    db_entry = db.collection("users").document(artist_name).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="User not found")

    r = requests.delete(
        "https://rostov-song-server.herokuapp.com/api/v1/songs/?song_id=" + song_id,
        headers=headers,
    )
    print(r)
    user_dict = db_entry.to_dict()
    user_dict["songs"].remove(song_id)
    print(user_dict)
    db.collection("users").document(artist_name).update(user_dict)
    print("OK")

    return song_id
