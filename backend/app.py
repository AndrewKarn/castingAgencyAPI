import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt
from urllib.request import urlopen
from auth.auth import requires_auth, AuthError
from database.models import setup_db, Movie, Actor

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.route('/')
def index():
    return 'Welcome!'
############### ROUTES ###############
# Actors
#########
@app.route('/actors')
@requires_auth('get:actors')
def get_actors(jwt):
    return jsonify({
        'actors': [actor.format() for actor in Actor.query.all()],
        'success': True,
    })


@app.route('/actors/<actor_id>', methods=['DELETE'])
@requires_auth('delete:actor')
def delete_actor(jwt, actor_id):
    actor_to_delete = Actor.query.get(actor_id)
    if actor_to_delete:
        actor_to_delete.delete()
        return jsonify({
            'success': True,
            'deleted': actor_id
        })
    else:
        abort(404)


@app.route('/actors', methods=['POST'])
@requires_auth('post:actor')
def add_actor(jwt):
    error = False
    data = request.get_json()
    name = data.get('name', '')
    age = data.get('age', '')
    gender = data.get('gender', '')
    exists = Actor.query.filter_by(
        name=name, age=age, gender=gender).one_or_none()
    actor_to_add = Actor(
        name=name,
        age=age,
        gender=gender
    )
    if not exists and gender and age and name:
        try:
            actor_to_add.insert()
        except:
            error = True
        finally:
            if not error:
                return jsonify({
                    'success': True,
                    'message': f'Actor: {name} was added'
                })
            else:
                actor_to_add.pull_back()
                return jsonify({
                    'success': False,
                    'message': f'Actor: {name} was not added'
                })
    else:
        abort(400)
        return jsonify({
            'success': False,
            'message': 'An actor with those attributes exists already or you are missing a field',
        })


@app.route('/actors/<actor_id>', methods=['PATCH'])
@requires_auth('patch:actors')
def update_actor(jwt, actor_id):
    request_data = request.get_json()
    new_name = request_data.get('name', False)
    new_age = request_data.get('age', False)
    new_gender = request_data.get('gender', False)
    actor_to_edit = Actor.query.get(actor_id)
    if actor_to_edit and new_name and new_gender and new_age:
        actor_to_edit.name = new_name
        actor_to_edit.age = new_age
        actor_to_edit.gender = new_gender
        actor_to_edit.update()
        return jsonify({
            'success': True,
            'message': 'Actor updated'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Unable to update actor'
        })


############### ROUTES ###############
# Movies
#####################################

@app.route('/movies')
@requires_auth('get:movies')
def get_movies(jwt):
    return jsonify({
        'movies': [movie.format() for movie in Movie.query.all()],
        'success': True,
    })


@app.route('/movies/<movie_id>', methods=['DELETE'])
@requires_auth('delete:movies')
def delete_movie(jwt, movie_id):
    movie_to_delete = Movie.query.get(movie_id)
    if movie_to_delete:
        movie_to_delete.delete()
        return jsonify({
            'success': True,
            'deleted': movie_id
        })
    else:
        abort(404)


@app.route('/movies', methods=['POST'])
@requires_auth('post:movies')
def add_movie(jwt):
    error = False
    data = request.get_json()
    title = data.get('title', False)
    release_date = data.get('release_date', False)
    exists = Movie.query.filter_by(
        title=title, release_date=release_date).one_or_none()
    movie_to_add = Movie(
        title=title,
        release_date=release_date
    )
    if not exists and title and release_date:
        try:
            movie_to_add.insert()
        except:
            error = True
        finally:
            if not error:
                return jsonify({
                    'success': True,
                    'message': f'Movie: {title} was added'
                })
            else:
                movie_to_add.pull_back()
                return jsonify({
                    'success': False,
                    'message': f'Movie: {title} was not added'
                })
    else:
        abort(409)
        return jsonify({
            'success': False,
            'message': 'A movie with those attributes exists already',
        })


@app.route('/movies/<movie_id>', methods=['PATCH'])
@requires_auth('patch:movies')
def update_movie(jwt, movie_id):
    request_data = request.get_json()
    new_title = request_data.get('title', '')
    new_release_date = request_data.get('release_date', '')
    movie_to_edit = Movie.query.get(movie_id)
    if movie_to_edit and new_title != '' and new_release_date:
        movie_to_edit.title = new_title
        movie_to_edit.release_date = new_release_date
        movie_to_edit.update()
        return jsonify({
            'success': True,
            'message': 'Movie updated'
        })
    else:
        abort(400)
        return jsonify({
            'success': False,
            'message': 'Unable to update movie'
        })


############### ROUTES ###############
# Error Handlers
#####################################


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resourceNotFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found."
    }), 404


@app.errorhandler(AuthError)
def handleAuthenticationerror(error):
    return jsonify({
        'success': False,
        'error': AuthError
    })


@app.errorhandler(404)
def resourceNotFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found."
    }), 404


@app.errorhandler(AuthError)
def handleAuthenticationerror(error):
    return jsonify({
        'success': False,
        'error': AuthError
    })
