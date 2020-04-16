# Casthing Agency API

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=app.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Tasks

### API Endpoints
N.B All endpoints require an access token, gets only require tier 1 access, the remaining require tiers 2 and 3.
## Get
# GET /movies
    ```bash
    returns all movies
    ```
# GET /actors
    ```bash
    returns all movies
    ```

## POST

# /movies
creates a new actor, example:
    ```bash
    {
      "title": "new_title",
      "release_date": "2020-15-20"
    }
    ```

# /actors
creates a new actor, exmaple request:
    ```bash
    {
      "name": "Hannah Carter",
      "age": 23,
      "gender": "Female"
    }
    ```
## PATCH
# /actor/<actor_id>
updates a specific actor based on id, all fields are required. Example request:
    ```bash
    {
      "name": "Drew Karn",
      "age": 23,
      "gender": "Male"
    }
    ```
## Delete
# /actors/<actor_id>
Deletes the actor based on specific id

# /movies
Deletes the movie based on the specified ids