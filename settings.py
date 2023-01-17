from os import getenv
from dotenv import load_dotenv

load_dotenv('.env')
BOT_TOKEN = getenv('BOT_TOKEN')
try:
    ADMINS = getenv('ADMINS')
    ADMINS = map(lambda x: x.strip(), ADMINS.split(","))
    ADMINS = list(map(lambda x: int(x), ADMINS))
except ValueError:
    ADMINS = [int(getenv("ADMINS")[:-1])]

API_ID = getenv("API_ID")
API_HASH = getenv("API_HASH")
SESSION = getenv("SESSION")

SQLALCHEMY_DATABASE_URI = 'sqlite:///bot.db?check_same_thread=False'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = getenv('SECRET_KEY')

DOMAIN = getenv('DOMAIN')
AUTH_TOKEN = getenv('AUTH_TOKEN')