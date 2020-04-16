import os
import unittest
import json
from database.models import setup_db, Movie, Actor, SQLAlchemy
from app import app

baseauth_token = os.getenv('TOKEN1')
second_level_auth_token = os.getenv('TOKEN2')
maxium_auth = os.getenv('TOKEN3')

class CastingAgencyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client
        self.database_name = "casting_test"
        self.database_path = os.getenv('DATABASE_URL')
        self.app.config['DEBUG'] = False
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {baseauth_token}' }
        self.actor_data = json.dumps({
            'name': 'Dana Smith',
            'age': 25,
            'gender': 'Female'
        })
        self.bad_actor_data = json.dumps({
            'name': '',
            'age': 251,
            'gender': 'Female'
        })

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.session.commit()
            self.db.drop_all()
            self.db.session.commit()
            self.db.create_all()
            self.db.session.query(Actor).delete()
            self.db.session.query(Movie).delete()
            self.db.session.commit()
##########################
# Get Tests
##########################
    def test_get_actors(self):
        res = self.client().get('/actors', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success', False), True)

    def test_bad_get_actors(self):
        self.headers['Authorization'] = 'aaaa'
        res = self.client().get('/actors', headers=self.headers)
        self.assertEqual(res.status_code, 401)

    def test_get_movies(self):
        res = self.client().get('/movies', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get('success', False))

    def test_bad_get_movies(self):
        self.headers['Authorization'] = 'aaaa'
        res = self.client().get('/movies', headers=self.headers)
        self.assertEqual(res.status_code, 401)



##########################
# POST Tests
##########################
    def test_post_actors_with_base_permission(self):
        res = self.client().post('/actors', headers=self.headers, data=self.actor_data)
        self.assertEqual(res.status_code, 401)

    def test_post_actor_as_director(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        res = self.client().post('/actors', headers=self.headers, data=self.actor_data)
        self.assertEqual(res.status_code, 200)
        exists = Actor.query.filter_by(name='Dana Smith', age=25, gender='Female').one_or_none()
        #confirm db save
        self.assertIsNotNone(exists)
        Actor.query.filter_by(name='Dana Smith', age=25, gender='Female').one().delete()

    def test_post_actor_as_executive(self):
        self.headers['Authorization'] = f'Bearer {maxium_auth}'
        res = self.client().post('/actors', headers=self.headers, data=self.actor_data)
        self.assertEqual(res.status_code, 200)
        exists = Actor.query.filter_by(name='Dana Smith', age=25, gender='Female').one_or_none()
        #confirm db save
        self.assertIsNotNone(exists)
        Actor.query.filter_by(name='Dana Smith', age=25, gender='Female').one().delete()

    def test_post_with_bad_data(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        res = self.client().post('/actors', headers=self.headers, data=self.bad_actor_data)
        self.assertEqual(res.status_code, 400)
        exists = Actor.query.filter_by(name='', age=251, gender='Female').one_or_none()
        #confirm db  did not save
        self.assertIsNone(exists)

    def test_post_movies_with_base_permission(self):
        res = self.client().post('/movies', headers=self.headers, data=self.actor_data)
        self.assertEqual(res.status_code, 401) 

    def test_post_movie_as_director(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        res = self.client().post('/movies', headers=self.headers, data=self.actor_data)
        self.assertEqual(res.status_code, 401)

    def test_post_movie_as_executive(self):
        self.headers['Authorization'] = f'Bearer {maxium_auth}'
        res = self.client().post('/movies', headers=self.headers, data=json.dumps({'title': 'gr8 movie', 'release_date': '2020-03-15'}))
        self.assertEqual(res.status_code, 200)
        exists = Movie.query.filter_by(title='gr8 movie', release_date='2020-03-15').one_or_none()
        #confirm db save
        self.assertIsNotNone(exists)
        Movie.query.filter_by(title='gr8 movie', release_date='2020-03-15').one().delete()
##########################################
# Patch
#     Tests  
##########################################

    def test_patch_as_executive(self):
        self.headers['Authorization'] = f'Bearer {maxium_auth}'
        Movie('example', '2020-04-15').insert()
        movie = Movie.query.first().format()
        self.assertEqual(movie.get('title', ''), 'example')
        movie_id = movie.get('id', '')
        updates = json.dumps({
            'title': 'new_title',
            'release_date': '2020-04-20'
        })
        res = self.client().patch(f'/movies/{movie_id}', data=updates, headers=self.headers)
        # Need the DB to sign off on this as well
        self.assertEqual(res.status_code, 200)
        self.assertEqual( Movie.query.get(movie_id).format().get('title', ''), 'new_title' )

    def test_patch_as_director(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        Movie('directors movie', '2020-04-15').insert()
        movie = Movie.query.first().format()
        self.assertEqual(movie.get('title', ''), 'directors movie')
        movie_id = movie.get('id', '')
        updates = json.dumps({
            'title': 'new_title_for_director',
            'release_date': '2020-04-20'
        })
        res = self.client().patch(f'/movies/{movie_id}', data=updates, headers=self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual( Movie.query.get(movie_id).format().get('title', ''), 'new_title_for_director' )
   
    def test_patching_movies_with_base_permission(self):
        updates = json.dumps({
            'title': 'new_title',
            'release_date': '2020-04-20'
        })
        res = self.client().patch('/movies/1', data=updates, headers=self.headers)

        self.assertEqual(res.status_code, 401)

    def test_patching_movies_with_bad_data(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        updates = json.dumps({
            'tite': '',
            'release_date': ''
        })
        res = self.client().patch('/movies/1', data=updates, headers=self.headers)

        self.assertEqual(res.status_code, 400)



##########################################
# Delete
#        Tests  
##########################################

    def test_delete_as_executive(self):
        self.headers['Authorization'] = f'Bearer {maxium_auth}'
        Movie('example', '2020-04-15').insert()
        movie = Movie.query.first().format()
        self.assertEqual(movie.get('title', ''), 'example')
        movie_id = movie.get('id', '')
        res = self.client().delete(f'/movies/{movie_id}', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get('success', False))
   
    def test_delete_movies_with_base_permission(self):
        Movie('example', '2020-04-15').insert()
        movie = Movie.query.first().format()
        self.assertEqual(movie.get('title', ''), 'example')
        movie_id = movie.get('id', '')
        res = self.client().delete(f'/movies/{movie_id}', headers=self.headers)
        self.assertEqual(res.status_code, 401)

    def test_delete_movies_as_director(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        Movie('example', '2020-04-15').insert()
        movie = Movie.query.first().format()
        self.assertEqual(movie.get('title', ''), 'example')
        movie_id = movie.get('id', '')
        res = self.client().delete(f'/movies/{movie_id}', headers=self.headers)
        self.assertEqual(res.status_code, 401)

    def test_delete_movies_with_bad_data(self):
        self.headers['Authorization'] = f'Bearer {maxium_auth}'
        res = self.client().delete('/movies/101', headers=self.headers)
        self.assertEqual(res.status_code, 404)


    def test_delete_actor_as_executive(self):
        self.headers['Authorization'] = f'Bearer {maxium_auth}'
        Actor('Hannah Carter', 23, 'Female').insert()
        actress = Actor.query.first().format()
        actress_id = actress.get('id', '')
        self.assertEqual(actress.get('name', ''), 'Hannah Carter')
        res = self.client().delete(f'/actors/{actress_id}', headers=self.headers)
        exists = Actor.query.filter_by(name='Hannah Carter', age=23, gender='Female').one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(exists)

    def test_delete_actor_as_director(self):
        self.headers['Authorization'] = f'Bearer {second_level_auth_token}'
        Actor('Hannah Carter', 23, 'Female').insert()
        actress = Actor.query.first().format()
        actress_id = actress.get('id', '')
        self.assertEqual(actress.get('name', ''), 'Hannah Carter')
        res = self.client().delete(f'/actors/{actress_id}', headers=self.headers)
        exists = Actor.query.filter_by(name='Hannah Carter', age=23, gender='Female').one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(exists)
    
    def test_delete_actor_as_assistant(self):
        Actor('Hannah Carter', 23, 'Female').insert()
        actress = Actor.query.first().format()
        actress_id = actress.get('id', '')
        self.assertEqual(actress.get('name', ''), 'Hannah Carter')
        res = self.client().delete(f'/actors/{actress_id}', headers=self.headers)
        exists = Actor.query.filter_by(name='Hannah Carter', age=23, gender='Female').one_or_none()
        self.assertEqual(res.status_code, 401)
        self.assertIsNotNone(exists)

if __name__ == "__main__":
    unittest.main()
