from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class SelectGameForm(FlaskForm):
    game_name = SelectField("Select game")
    submit = SubmitField("Go!")


class BaseSubmitForm(FlaskForm):
    submit = SubmitField("Submit")
