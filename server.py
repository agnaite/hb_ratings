"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
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

@app.route('/user_profile/<user_id>')
def show_user_profile(user_id):
    """Show user profile"""
    
    current_user = User.query.get(user_id)
    age = current_user.age
    zipcode = current_user.zipcode
    ratings = current_user.ratings
    email = current_user.email
    
    user_ratings = {}

    for item in ratings:
        score = item.score
        movie_title = Movie.query.get(item.movie_id).title
        user_ratings[movie_title] = score
 
    return render_template('user_profile.html', email=email, age=age, zipcode=zipcode, ratings=user_ratings)

@app.route('/movies')
def movie_list():
    """Show list of movies"""

    movies = db.session.query(Movie).order_by(Movie.title).all()

    return render_template('movie_list.html', movies=movies)

@app.route('/movie_details/<movie_id>', methods=['POST', 'GET'])
def show_movie_details(movie_id):
    """Show movie details"""

    current_movie = Movie.query.get(movie_id)

    title = current_movie.title
    released_at = current_movie.released_at
    url = current_movie.imdb_url
    ratings = current_movie.ratings

    movie_ratings = []

    for item in ratings:
        score =item.score
        movie_ratings.append(score)

    average_score = sum(movie_ratings) / len(movie_ratings)


    return render_template('movie_details.html', title=title, released_at=released_at, url=url, movie_ratings= movie_ratings,
                            average_score=average_score, movie_id = movie_id)

@app.route('/process_score', methods=['POST'])
def process_score():
    user_score = request.form.get('score')
    movie_id = request.form.get('movie_id')
    old_rating = db.session.query(Rating).filter_by(movie_id=movie_id, user_id=session['logged_in']).first()
    all_scores_list = []

    if old_rating != None:
        old_rating.score = user_score
        db.session.commit()
        all_scores = db.session.query(Rating).filter_by(movie_id=movie_id).all()
        for item in all_scores:
            all_scores_list.append(item.score)
        return jsonify({'scores': all_scores_list, 'msg': "Your score has been updated!"})
    else:
        new_rating = Rating(movie_id=movie_id, user_id=session['logged_in'], score=user_score)
        db.session.add(new_rating)
        db.session.commit()
        all_scores = db.session.query(Rating).filter_by(movie_id=movie_id).all()
        for item in all_scores:
            all_scores_list.append(item.score)
        return jsonify({'scores': all_scores_list, 'msg': "Your score has been added!"})

@app.route('/register_form')
def register_form():

    return render_template('register.html')


@app.route('/process_registration', methods=['POST'])
def process_registration():

    user_email = request.form.get('email')
    password = request.form.get('password')
    zipcode = request.form.get('zipcode')
    age = request.form.get('age')

    user_exists = User.query.filter_by(email=user_email).first() 

    if user_exists != None:
        flash('Your email is already registered. Please login.')
        return redirect('/login')
    else:
        new_user = User(email=user_email, password=password, age=age, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()

        flash("Your account has been successfully created!")
        session['logged_in'] = new_user.user_id

        return redirect('/')


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
        session['logged_in'] = user_exists.user_id
        return redirect('/')
    elif user_exists != None and user_exists.password != password:
        flash('Incorrect password. Please reenter.')
        return redirect('/login')
    else:
        flash('User account not found. Please register.')
        return redirect('/register_form')

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
