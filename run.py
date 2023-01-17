from logger import logger
from settings import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from app import app, db
from waitress import serve

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    logger.info("Starting app")
    #app.run(port=6575, debug=True)
    serve(app, port=6575)
