from datetime import datetime as dt
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    DecimalField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired, NumberRange, ValidationError


def dropdownDefaultValidator(form, field):
    if field.data == "-1":
        raise ValidationError("Please select an option")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

    submit = SubmitField("Login")
