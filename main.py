import os
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db

app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config['SECRET_KEY'] = "haveAgoodDay"
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

#Import all the controllers so they are loaded
from application.controllers import *

if __name__ == "__main__":
    #Run the flask app
    app.run(host='0.0.0.0', port=5000)