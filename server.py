"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()

    return render_template('user_list.html', users=users)

@app.route('/login')
def login_user():
    """Allows user to input name and password"""


    return render_template('login_form.html')

@app.route('/process_login', methods=['POST'])
def process_login():
    """Checks if user already exists and allows them to login"""

    user_email = request.form.get('email')
    password = request.form.get('password')

    user_exists = User.query.filter_by(email=user_email).first() 

    if user_exists != None and user_exists.password == password:
        flash('Successfully logged in!')
        session['logged_in'] = user_email
        return redirect('/')
    elif user_exists != None and user_exists.password != password:
        flash('Incorrect password. Please reenter.')
        return redirect('/login')
    else:
        flash('User account not found. Please register.')
        return redirect('/login')

@app.route('/logout')
def process_logout():
    """Log out user"""

    del session['logged_in']
    flash("You are successfully logged out!")

    return redirect('/')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
