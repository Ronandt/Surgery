from wtforms import Form, StringField, SelectField, BooleanField, validators, PasswordField, IntegerField
from wtforms.fields import EmailField
from wtforms.fields.simple import TextAreaField

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

class AddFundsForm(Form):
    amount = IntegerField("Enter Amount: ", [validators.NumberRange(min = 1, max = 10000000), validators.DataRequired()], render_kw={"placeholder" : "100"})
    password = PasswordField("Enter Password:", [validators.Length(min = 6, max=35), validators.DataRequired()])

class EditUser(Form):
    amount = IntegerField("Update Balance: ", [validators.NumberRange(min = 0, max = 10000000)])
    email = EmailField("Update Email: ", [validators.DataRequired(), validators.Length(min=10, max=150)])
    username = StringField("Update Username: ", [validators.DataRequired(), validators.Length(min = 2, max = 40)])
    gender = SelectField('Update Gender', choices=[('F', "Female"), ('M', "Male")])
    password = PasswordField('Update Password', [validators.Length(min=6, max=35), validators.DataRequired()])
    permission = IntegerField("Update Permissions: ", [validators.NumberRange(min = 0, max = 1), validators.DataRequired()])

class AddNotes(Form):
    title = StringField("Enter title: ", [validators.Length(min=2, max=40), validators.DataRequired()])
    description = TextAreaField("Enter description: ", [validators.Length(min = 1, max= 300), validators.DataRequired()], render_kw={"rows": 5, "cols": 10})

class TicketForm(Form):
    title = StringField("Title: ", [validators.Length(min = 2, max = 30), validators.DataRequired()])
    issue = SelectField("Issue Faced: ", choices = [('Ordering', 'Ordering'), ('Navigation', 'Navigation'), ('Bug', 'Bug'), ('Other', 'Other')])
    severity = SelectField("Severity Level: ", choices = [('Low', "Low"), ("Medium",  "Medium"), ("High", "High")])
    description = TextAreaField("Description ", [validators.Length(min = 10, max= 3000), validators.DataRequired()], render_kw = {"rows" : 10, 'cols' : 10})

    
class AddUser(Form):
    amount = IntegerField("Add Balance: ", [validators.NumberRange(min = 0, max = 10000000)])
    email = EmailField("Add Email: ", [validators.DataRequired(), validators.Length(min=10, max=150)])
    username = StringField("Add Username: ", [validators.DataRequired(), validators.Length(min = 2, max = 40)])
    gender = SelectField('Add Gender', choices=[('F', "Female"), ('M', "Male")])
    password = PasswordField('Add Password', [validators.Length(min=6, max=35), validators.DataRequired()])
    permission = IntegerField("Add Permissions: ", [validators.NumberRange(min = 0, max = 1), validators.DataRequired()])

class FeedbackForm(Form):
    title = StringField("Title: ", [validators.Length(min = 2, max = 30), validators.DataRequired()])
    remarks = TextAreaField("Other remarks ", [validators.Length(min = 10, max= 3000), validators.DataRequired()], render_kw = {"rows" : 10, 'cols' : 10})
    improvement = TextAreaField("How else can we improve", [validators.Length(min = 10, max= 300), validators.DataRequired()], render_kw = {"rows" : 5, 'cols' : 5})
    favourite = StringField("Favourite thing", [validators.Length(min = 2, max = 50), validators.DataRequired()])
    least_favourite = StringField("Least favourite thing", [validators.Length(min = 2, max = 50), validators.DataRequired()])

class UpdateUserForm(Form):
    email = EmailField("Update Email: ", [validators.DataRequired(), validators.Length(min=10, max=150)])
    username = StringField("Update Username: ", [validators.DataRequired(), validators.Length(min = 2, max = 40)])
    gender = SelectField('Update Gender', choices=[('F', "Female"), ('M', "Male")])
    password = PasswordField('Update Password', [validators.Length(min=6, max=35), validators.DataRequired()])
    repeat_password = PasswordField('Repeat Password', [validators.Length(min=6, max=35), validators.DataRequired()])