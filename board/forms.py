from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, IntegerField, FieldList
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from flask_login import current_user
from board.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Define custom validation methods to make sure username and email are not taken

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            
class CalendarDateField(DateField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super(CalendarDateField, self).__init__(label, validators, format, **kwargs)

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('To Do', 'To Do'), ('In Progress', 'In Progress'), ('Done', 'Done')])
    due_date = CalendarDateField('Due Date', validators=[DataRequired()])
    priority = IntegerField('Priority', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Submit')


class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    member_emails = StringField('Member Emails', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # Define custom validation method to make sure all member emails are valid

    def validate_member_emails(self, member_emails):
        member_emails = member_emails.data.split(',')
        for email in member_emails:
            user = User.query.filter_by(email=email).first()
            if not user:
                raise ValidationError(f'User with email {email} does not exist in the system. Please enter a valid email.')