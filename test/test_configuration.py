import unittest

import rest_client
from rest_client import RESTConfiguration, RestClientConfigurationError
from rest_client import QueryParameter, BodyParameter, EndPoint


class TestMinimal(unittest.TestCase):

	def test_minimal_config(self):
		'''
		check method or path
		'''
		
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET')
		Config()

		class Config (RESTConfiguration):
			ep = EndPoint(path=['test'], method='GET')
		Config()
	
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=['test'], method='ERR')
			Config()

		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=3, method='GET')
			Config()


class TestParameters(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_good_query_parameters(self):
		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET',
						  parameters={
							  'para': QueryParameter(name="sort",
													 default='some_default',
													 description='description',
                                ),
                            }
                 )
		Config()

		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET',
						  parameters={
							  'para': QueryParameter(name="sort",
													 required=False,
                                ),
                            }
                 )
		conf = Config()


	def test_bad_query_parameters(self):
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 required=3
                                 ),
                                    }
                  )
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 multiple=3
                                 ),
                                    }
                  )
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 exclusion_group=3
                                 ),
                                    }
                  )
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 default='some_default',
														 required=True
									),
								}
					 )

	def test_exclusion_group(self):
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 exclusion_group='\n',
                                 ),
                                    }
                  )

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 default='x',
														 choices=['a', 'b'],
                                                                  ),
                                    }
                  )

	# --------------------------------------------------------------
	def test_choices(self):
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 choices='some_default',
									),
								}
					 )

	# --------------------------------------------------------------
	def test_descriptions(self):
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': QueryParameter(name="sort",
														 description=3,
                                 ),
                                    }
                  )

	# --------------------------------------------------------------
	def test_bad_body_parameters(self):
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={
								  'para': BodyParameter(name="sort"),
                                    }
                  )
		
class TestEndpoint(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	# --------------------------------------------------------------
	def test_bad_init_parameters(self):
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  description=3
                  )

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  path_description=3
                  )
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  headers='none'
                  )
	
	# --------------------------------------------------------------
	def test_no_endpoints(self):
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				default_headers = {'x': 'y', }
			c = Config()
			c.get_list_of_endpoints()

	def test_bad_rest_parameters(self):
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters='x'
                  )
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters='x'
                  )

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  parameters={'x': 'y', }
                  )

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  return_class='error'
                  )

	def test_bad_endpoints(self):
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				data = EndPoint(path=[''], method='GET')
			Config()


	def test_bad_defaults(self):
		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET')
				default_headers = 'error'
			Config()

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET')
				default_headers = {'key': 3},
			Config()

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET')
				default_headers = {'key': None},
			Config()


	def test_good_defaults(self):
		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET')
			default_headers = {'key': 'val'}
		Config()

		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET', headers={'key': 'oldval', })
			default_headers = {'key': 'val'}
		conf = Config()
		self.assertDictEqual(conf.endpoints['ep'].headers, {'key': 'oldval'})

		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET', headers={'otherkey': 'val', })
			default_headers = {'key': 'val'}
		conf = Config()
		self.assertDictEqual(conf.endpoints['ep'].headers, {'key': 'val', 'otherkey': 'val'})
		

	def test_descriptions(self):
		# --------------------------------------------------------------

		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET',
						  description="OK")
		conf = Config()

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  description=3)
			Config()

			# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep = EndPoint(path=[''], method='GET',
						  path_description={'x': 'y', })
			Config()

		# --------------------------------------------------------------
		with self.assertRaises(RestClientConfigurationError):
			class Config(RESTConfiguration):
				ep = EndPoint(path=[''], method='GET',
							  path_description=3)
			Config()

		

	def test_introspection(self):
		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep1 = EndPoint(path=[''], method='GET',
						   parameters={'p1': QueryParameter('p1'),
									   'p2': QueryParameter('p2', multiple=True),
									   'p3': QueryParameter('p3', required=True),
									   'p4': QueryParameter('p4', default='def'),
                     }
                  )

		c = Config()
		expected = {'required': ['p3'], 'optional': ['p1', 'p2', 'p4'], 'multiple': ['p2']}
		self.assertDictEqual(c.ep1.query_parameters, expected)

		self.assertListEqual(c.ep1.all_query_parameters, ['p1', 'p2', 'p4', 'p3'])
		self.assertListEqual(c.ep1.required_parameters, ['p3'])
		self.assertListEqual(c.ep1.multiple_parameters, ['p2'])
		self.assertListEqual(c.ep1.all_parameters, ['p1', 'p2', 'p4', 'p3'])

		self.assertDictEqual(c.ep1.as_dict, {'required': ['p3'], 'optional': ['p1', 'p2', 'p4']})
		self.assertDictEqual(c.ep1.defaults, {'p4': 'def'})

		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep1 = EndPoint(path=[''], method='GET',
						   parameters={'p1': QueryParameter('p1'),
									   'p2': QueryParameter('p2', multiple=True, exclusion_group='a'),
									   'p3': QueryParameter('p3', required=True, exclusion_group='a'),
									   'p4': QueryParameter('p4'),
                     }
                  )

		c = Config()
		expected = {'a': ['p2', 'p3']}
		self.assertDictEqual(c.ep1.query_parameter_groups, expected)
		
		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep1 = EndPoint(path=['x', 'y', 'z'], method='GET')

		c = Config()
		expected = []
		self.assertListEqual(expected, c.ep1.path_parameters)

		# --------------------------------------------------------------
		class Config(RESTConfiguration):
			ep1 = EndPoint(path=['x', '{y}', 'z'], method='GET')

		c = Config()
		expected = ['y']
		self.assertListEqual(expected, c.ep1.path_parameters)
