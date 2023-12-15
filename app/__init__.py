import sentry_sdk
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
      "ix": "ix_%(column_0_label)s",
      "uq": "uq_%(table_name)s_%(column_0_name)s",
      "ck": "ck_%(table_name)s_%(constraint_name)s",
      "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
      "pk": "pk_%(table_name)s"
    })


sentry_sdk.init(dsn="https://eeb52daec704814c1f45735df76cf773@o4506381594525696.ingest.sentry.io/4506381604093952",
                traces_sample_rate=1.0,
                profiles_sample_rate=1.0,
                )

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///games.db"


db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

from app.custom import bp_custom
app.register_blueprint(bp_custom)

from app.scoring import bp_game_scoring
app.register_blueprint(bp_game_scoring)

from app.auth import bp_auth
app.register_blueprint(bp_auth)

from app.profile import bp_profile
app.register_blueprint(bp_profile)

from app import routes
from app import models
