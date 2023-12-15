from flask import Blueprint


bp_game_scoring = Blueprint("scoring", __name__, template_folder="templates")


from app.scoring import routes
