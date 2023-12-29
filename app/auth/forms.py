from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from app.models import User
from app import db


class LoginForm(FlaskForm):
    username = StringField("Username", [DataRequired(), Length(max=64)])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    username = StringField("Username", [DataRequired(), Length(max=64)])
    email = EmailField("Email", [DataRequired(), Length(max=150)])
    bgg_username = StringField("BoardGameGeek username (optional)", [Length(max=120)])
    password = PasswordField("Password", [DataRequired()])
    password2 = PasswordField("Repeat password", [DataRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

    def validate_username(self, username):
        user = db.session.scalar(db.select(User).filter_by(username=username.data))
        if user is not None:
            raise ValidationError("Please choose another username")

    def validate_email(self, email):
        user = db.session.scalar(db.select(User).filter_by(email=email.data))
        if user is not None:
            raise ValidationError("A user with this email is already registered")


class EditUserForm(FlaskForm):
    username = StringField("Username", [DataRequired(), Length(max=64)])
    email = EmailField("Email", [DataRequired(), Length(max=150)])
    bgg_username = StringField("BoardGameGeek username (optional)")
    submit = SubmitField("Submit")

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(db.select(User).filter_by(username=username.data))
            if user is not None:
                raise ValidationError("Please choose another username")

    def validate_email(self, email):
        if email.data != self.original_email:
            user = db.session.scalar(db.select(User).filter_by(email=email.data))
            if user is not None:
                raise ValidationError("A user with this email is already registered")


class ChangePasswordRequestForm(FlaskForm):
    email = StringField("Email", [DataRequired(), Length(max=150)])
    submit = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("New password", [DataRequired()])
    password2 = PasswordField("Repeat new password", [DataRequired(), EqualTo("password")])
    submit = SubmitField("Submit")
