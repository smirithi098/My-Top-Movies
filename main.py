import os
from dotenv import load_dotenv
import requests
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from forms import AddForm, EditForm

load_dotenv()

MOVIE_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie"
KEY = os.environ.get("API_KEY")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
Bootstrap(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movies.db"
db = SQLAlchemy(app)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=False)


@app.route("/")
def home():
    all_movies = db.session.query(Movies).all()
    return render_template('home.html', data=all_movies)


@app.route('/view')
def view():
    movie_id = request.args.get("id")
    data = Movies.query.get(movie_id)
    return render_template("view.html", movie=data)


@app.route("/add", methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        req_params = {
            "api_key": KEY,
            "language": "en - US",
            "query": form.movie_field.data
        }
        response = requests.get(url=MOVIE_SEARCH_URL, params=req_params)
        list_of_movies = response.json()['results']
        return render_template("select.html", movies=list_of_movies)
    return render_template("add.html", form=form)


@app.route("/get-movie")
def get_movie_details():
    movie_id = request.args.get('id')
    req_params = {
        "api_key": KEY,
        "language": "en - US"
    }
    response = requests.get(url=f"{MOVIE_DETAILS_URL}/{movie_id}", params=req_params)
    movie_data = response.json()
    new_movie = Movies(
        title=movie_data['title'],
        year=movie_data['release_date'].split('-')[0],
        description=movie_data['overview'],
        img_url=f"{MOVIE_IMAGE_URL}{movie_data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("update", id=new_movie.id))


@app.route("/edit", methods=["POST", "GET"])
def update():
    form = EditForm()
    movie_id = request.args.get('id')
    movie_to_update = Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.rating = form.rating_field.data
        movie_to_update.review = form.review_field.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, title=movie_to_update.title)


@app.route("/delete-movie")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
