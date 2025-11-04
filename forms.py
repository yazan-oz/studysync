from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    submit = SubmitField('Login')

from wtforms import TextAreaField, DateTimeLocalField, SelectField, BooleanField

class TaskForm(FlaskForm):
    title = StringField('Task Title', 
                       validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    due_date = DateTimeLocalField('Due Date', format='%Y-%m-%dT%H:%M', validators=[])
    priority = SelectField('Priority', 
                          choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                          default='medium')
    class_id = SelectField('Class', coerce=int, validators=[])
    completed = BooleanField('Completed')
    submit = SubmitField('Save Task')

from wtforms import StringField, TextAreaField, SubmitField, URLField

class ClassForm(FlaskForm):
    name = StringField('Class Name', 
                      validators=[DataRequired(), Length(min=1, max=100)])
    code = StringField('Course Code', 
                      validators=[Length(max=50)])
    professor = StringField('Professor', 
                          validators=[Length(max=100)])
    room = StringField('Room/Location', 
                      validators=[Length(max=50)])
    color = StringField('Color', 
                       validators=[Length(max=7)],
                       default='#3498db')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Class')

class ClassLinkForm(FlaskForm):
    title = StringField('Link Title', 
                       validators=[DataRequired(), Length(min=1, max=100)])
    url = URLField('URL', 
                  validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Add Link')