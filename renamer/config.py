from os import getenv
from dotenv import load_dotenv


def get_data():
    load_dotenv('.env')

    API_ID = getenv("API_ID")
    API_HASH = getenv("API_HASH")
    SESSION = getenv("SESSION")

    return API_ID, API_HASH, SESSION