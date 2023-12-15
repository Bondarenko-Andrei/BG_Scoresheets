from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList
from wtforms.validators import DataRequired, Optional


class SearchGameForm(FlaskForm):
    game_name = StringField("Game name", [DataRequired()])
    search = SubmitField("Search")


class BggIdForm(FlaskForm):
    bgg_id = IntegerField("BGG ID", [DataRequired()])
    submit = SubmitField("Submit")


class CustomSetFieldsForm(FlaskForm):
    fields = FieldList(StringField("Field name", [DataRequired()]), min_entries=1)
    submit = SubmitField("Submit")


class CustomCreate(FlaskForm):
    name = StringField("Game name (required)", [DataRequired()])
    min_players = IntegerField("Min # of players", [Optional()])
    max_players = IntegerField("Max # of players", [Optional()])
    year = IntegerField("Year published", [Optional()])
    fields = FieldList(StringField("Field name", [DataRequired()]), min_entries=1)
    submit = SubmitField("Submit")
