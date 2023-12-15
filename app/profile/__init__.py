from flask import Blueprint

bp_profile = Blueprint('profile', __name__, template_folder="templates", url_prefix="/user")

from app.profile import routes
