from flask_wtf import FlaskForm
from wtforms import FieldList, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional


class UserPlayersForm(FlaskForm):
    players = FieldList(StringField())
    new_players = FieldList(StringField("name", [DataRequired()]))
    submit = SubmitField('Submit')


class EditFieldsForm(FlaskForm):
    fields = FieldList(StringField("name", [DataRequired()]))
    new_fields = FieldList(StringField("name", [DataRequired()]))
    submit = SubmitField("Submit")


class EditCustomGame(EditFieldsForm):
    name = StringField("Game name (required)", [DataRequired()])
    min_players = IntegerField("Min # of players", [Optional()])
    max_players = IntegerField("Max # of players", [Optional()])
    year = IntegerField("Year published", [Optional()])


class SubmitForm(FlaskForm):
    submit = SubmitField("Submit")
