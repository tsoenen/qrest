from pprint import pprint
import unittest

import rest_client
from rest_client import APIConfig, RestClientConfigurationError
from rest_client import QueryParameter, BodyParameter, ResourceConfig
from rest_client import JSONResource
from rest_client.auth import UserPassAuthConfig


class JsonPlaceHolderConfig(APIConfig):
	url = 'https://jsonplaceholder.typicode.com'
	default_headers = {"Content-type": "application/json; charset=UTF-8"}
	
	all_posts = ResourceConfig(path=['posts'],
							   method='GET',
							   description='retrieve all posts'
                            )

	filter_posts = ResourceConfig(path=['posts'],
							   method='GET',
							   description='retrieve all posts by filter criteria',
							   parameters={
								   'user_id': QueryParameter(name='userId',
														  required=False,
														  # default='',
														  # choices=[],
														  description='the user Id that made the post'),
            }
        )

	single_post = ResourceConfig(path=['posts', '{item}'],
								 method='GET',
								 description='Retrieve a single post',
								 path_description={'item': 'select the post ID to retrieve',
                           },
            headers={'X-test-post': 'qREST python ORM', }
        )

	comments = ResourceConfig(path=['posts', '{post_id}', 'comments'],
								 method='GET',
								 description='Retrieve comments for a single post',
								 path_description={'post_id': 'select the post ID to retrieve', }
                           )

	create_post = ResourceConfig(path=['posts', ],
								 method='POST',
								 description='Create a new post',
								 parameters={
									 'title': BodyParameter(name='title',
															required=True,
															# default='',
															# choices=[],
															description='The title of the post'),
  									 'content': BodyParameter(name='body',
															  required=True,
															  # default='',
															  # choices=[],
															  description='The title of the post'),
  									 'user_id': BodyParameter(name='userId',
															  required=False,
															  default=101,
															  # choices=[],
															  description='The id of the user creating the post'),
        }
        )

class TestJsonPlaceHolderGet(unittest.TestCase):

	def setUp(self):
		self.config = JsonPlaceHolderConfig()
		x = 1

	def test_get_all_posts(self):
		'''
		check method or path
		'''
		x = rest_client.API(self.config)
		response = x.all_posts.fetch()
		self.assertIsInstance(response, list)
		self.assertEqual(len(response), 100)

	def test_get_post_1(self):
		'''
		check method or path
		'''
		x = rest_client.API(self.config)
		response = x.single_post.fetch(item=1)
		self.assertIsInstance(response, dict)
		self.assertEqual(len(response), 4)

	def test_filter_posts_fetch(self):
		'''
		check method or path
		'''
		x = rest_client.API(self.config)
		response = x.filter_posts.fetch(user_id=1)
		self.assertIsInstance(response, list)
		self.assertEqual(len(response), 10)

	def test_filter_posts_response(self):
		'''
		check method or path
		'''
		x = rest_client.API(self.config)
		resource = x.filter_posts(user_id=1)
		response = resource.data

		self.assertIsInstance(response, list)
		self.assertEqual(len(response), 10)

	def test_posts_comments(self):
		'''
		check method or path
		'''
		x = rest_client.API(self.config)
		response = x.comments.fetch(post_id=1)
		self.assertIsInstance(response, list)
		self.assertEqual(len(response), 5)



class TestJsonPlaceHolderPost(unittest.TestCase):

	def setUp(self):
		self.config = JsonPlaceHolderConfig()
		x = 1

	def test_new_post(self):
		'''
		create a new post
		'''
		x = rest_client.API(self.config)
		print(x.create_post.help('title'))

		title = "new post using qREST ORM"
		content = 'this is the new data posted using qREST'
		user_id = 200

		# send data to jsonplaceholder server
		response = x.create_post(title=title, content=content, user_id=user_id)
		self.assertIsInstance(response.data, dict)

		self.assertEqual(response.data['userId'], user_id)

		# also test using default values
		response = x.create_post(title=title, content=content)
		self.assertIsInstance(response.data, dict)

		self.assertEqual(response.data['userId'], 101)
		
