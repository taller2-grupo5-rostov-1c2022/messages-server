import firebase_admin
import json
from firebase_admin import credentials
from firebase_admin import auth

from dotenv import load_dotenv

from src.constants import TESTING
from src.mocks.firebase.auth import auth_mock

load_dotenv()

_auth = auth_mock

if TESTING is None:
    # Use a service account
    with open("google-credentials.json") as json_file:
        cert_dict = json.load(json_file, strict=False)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(cred)

    _auth = auth


def get_auth():
    return _auth
