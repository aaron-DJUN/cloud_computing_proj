from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
#from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from psrPlatform.models import Users, Products, Ratings


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(reviewerName=username.data).first()
        print(Users.query.filter_by(reviewerName=username.data))
        if user:
            raise ValidationError('That username already exists. Please use another username to register. ')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class RateForm(FlaskForm):
    game_id =  TextAreaField('Game ID ?', validators=[DataRequired()])
    score = RadioField('Rate', choices =[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')],validators=[DataRequired()] )
    comment = TextAreaField('Cound you please give some comment?', validators=[DataRequired()])
    summary = TextAreaField('If you want, you can add one summary here?')
    submit = SubmitField('Submit')

class PicForm(FlaskForm):
    picture = FileField('Please upload the picture', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Search')