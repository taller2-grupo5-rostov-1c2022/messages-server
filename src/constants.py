import os

API_KEY = os.environ.get("API_KEY", "key")
API_KEY_NAME = "api_key"
TESTING = os.environ.get("TESTING", None)
SUPPRESS_BLOB_ERRORS = False
STORAGE_PATH = "https://storage.googleapis.com/rostov-spotifiuby.appspot.com/"
