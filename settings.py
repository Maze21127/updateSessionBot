from os import getenv
from dotenv import load_dotenv

load_dotenv('.env')
BOT_TOKEN = getenv('BOT_TOKEN')
ADMINS = getenv('ADMINS')
ADMINS = map(lambda x: x.strip(), ADMINS.split(","))
ADMINS = list(map(lambda x: int(x), ADMINS))

API_ID = getenv("API_ID")
API_HASH = getenv("API_HASH")
SESSION = getenv("SESSION")
