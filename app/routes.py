from flask import render_template
from app import app, db


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
