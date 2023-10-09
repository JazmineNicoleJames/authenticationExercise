from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
        username = StringField("Username", validators=[InputRequired()])
        password = PasswordField("Password", validators=[InputRequired()])
        email = StringField("Email address", validators=[InputRequired()])
        first_name = StringField("First name", validators=[InputRequired()])
        last_name = StringField("Last name", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = StringField("Content", validators=[InputRequired()])


class DeleteForm(FlaskForm):
    """Empty."""