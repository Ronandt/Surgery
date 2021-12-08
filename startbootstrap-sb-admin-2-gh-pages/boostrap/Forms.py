from wtforms import Form, StringField, SelectField, BooleanField, validators, PasswordField
from wtforms.fields import EmailField

class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=2, max=40), validators.DataRequired()])
    gender = SelectField('Gender', choices=[('F', "Female"), ('M', "Male")], default="")
    email = EmailField('Email', [validators.Length(min=10, max=150), validators.DataRequired()])
    password = PasswordField('Create Password', [validators.Length(min=6, max=35), validators.DataRequired()])
    repeat_password = PasswordField('Repeat Password', [validators.Length(min=6, max=35), validators.DataRequired()])
    tos = BooleanField('Do you agree to the terms and conditions', validators=[validators.DataRequired()])

class LoginForm(Form):
    username = StringField("", [validators.Length(min=2, max=40), validators.DataRequired()], render_kw={"placeholder" : "Enter Username"})
    password = PasswordField('', [validators.Length(min=6, max=35), validators.DataRequired()], render_kw={"placeholder" : "Enter Password"})

class StaffForm(Form): #implmentation will be later
    
    username = StringField("", [validators.Length(min=2, max=40), validators.DataRequired()], render_kw={"placeholder" : "Enter Username"})
    password = PasswordField('', [validators.Length(min=6, max=35), validators.DataRequired()], render_kw={"placeholder" : "Enter Password"})
    