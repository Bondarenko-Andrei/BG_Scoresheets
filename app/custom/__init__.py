from flask import Blueprint


bp_custom = Blueprint("custom", __name__, template_folder="templates")


from app.custom import routes
