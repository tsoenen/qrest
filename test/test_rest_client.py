import unittest
import bcs_rest_client as client
from bcs_rest_client.conf import RESTConfig, EndPointConfig, BodyParameter, QueryParameter,  ParameterConfig
from bcs_rest_client.auth import UserPassAuthConfig

class MinimalConfig(RESTConfig):
    endpoint1 = EndPointConfig(path=[], method='GET')

class UserPassConfig(RESTConfig):
    endpoint1 = EndPointConfig(path=[], method='GET')
    authentication = UserPassAuthConfig(verify_ssl=False)


class TestInvalidResourceError(unittest.TestCase):
    
    def test_raise(self):
        from bcs_rest_client.utils import InvalidResourceError
        
        def broken_function():
            name = 'rest client name'
            resource = 'resource_name'
            raise InvalidResourceError(name, resource)
        
        with self.assertRaises(InvalidResourceError):
            broken_function()

    def test_try(self):
        from bcs_rest_client.utils import InvalidResourceError
        
        try:
            name = 'rest client name'
            resource = 'resource_name'
            raise InvalidResourceError(name, resource)
        except InvalidResourceError as e:
            expected = '"\'resource_name\' is not a valid resource for \'rest client name\'"'
            received = str(e)
            self.assertEqual(expected, received)
            
        
            
class TestRestClient(unittest.TestCase):

    url = "https://example.com"

    def test_string_contract(self):

        contract = client.string_type
        contract.check("")
        contract.check("123")
        contract.fail(None)
        contract.fail(123)
        contract = client.string_type_or_none
        contract.check("")
        contract.check("123")
        contract.check(None)
        contract.fail(123)

    def test_login_user(self):
        from bcs_rest_client.auth import BasicAuthentication

        rc = client.RestClient(url=self.url, config=UserPassConfig)
        self.assertIsInstance(rc.auth, BasicAuthentication)
        rc.auth.login(username="test")
        self.assertEqual(rc.auth.login_tuple, ('test', None))
        rc.auth.login(username="test", password=None)
        self.assertEqual(rc.auth.login_tuple, ('test', None))
        rc.auth.login(username="test", password='pass')
        self.assertEqual(rc.auth.login_tuple, ('test', 'pass'))

    def test_login_pass_no_user(self):
        from bcs_rest_client.auth import BasicAuthentication
        from bcs_rest_client.exception import BCSRestLoginError
        rc = client.RestClient(url=self.url, config=UserPassConfig)
        
        try:
            rc.auth.login(username=None, password='pass')
        except BCSRestLoginError:
            pass

    @unittest.expectedFailure
    def test_init_wrong_type(self):

        client.RestClient(url=self.url, user=123)

    def test_init_resources(self):
        from bcs_rest_client.conf import RESTConfig, EndPointConfig, BodyParameter, QueryParameter

        rc = client.RestClient(url=self.url, config=MinimalConfig)
        self.assertEqual(rc.resources, ['endpoint1'])
        
        class TestConfig(RESTConfig):
            some_function_name = EndPointConfig(path=["some", "collection", "{id}"],
                                                method="GET",
                                                parameters={
                                                    'some_parameter': QueryParameter("some_parameter"),
                                                    'alias': QueryParameter(name="alias", exclusion_group="likeSearch"),
                                                    'markerUid': QueryParameter(name="markerUid", exclusion_group="likeSearch"),
                                                    'breedingContactEmployeeId': QueryParameter(name="breedingContactEmployeeId", exclusion_group="exact", required=True),
                                                    'researchContactEmployeeId': QueryParameter(name="researchContactEmployeeId", exclusion_group="exact", required=True),
                                                }
                                                )
        rc = client.RestClient(url=self.url, config=TestConfig)
        self.assertEqual(rc.resources, ['some_function_name'])
        self.assertEqual(len(rc.resources), 1)
        self.assertEqual(len(rc.some_function_name.parameters), 2)
        self.assertEqual(len(rc.some_function_name.config.path_parameters), 1)
        self.assertEqual(len(rc.some_function_name.config.query_parameters["optional"]), 3)
        self.assertEqual(len(rc.some_function_name.config.query_parameters["required"]), 2)
        self.assertEqual(len(rc.some_function_name.config.query_parameter_groups), 2)
        
        # also test direct addressing
        f = rc.some_function_name
        self.assertEqual(len(f.parameters), 2)
        self.assertEqual(len(f.config.path_parameters), 1)
        self.assertEqual(len(f.config.query_parameters["optional"]), 3)
        self.assertEqual(len(f.config.query_parameters["required"]), 2)
        self.assertEqual(len(f.config.query_parameter_groups), 2)
        self.assertEqual(len(f.config.multiple_parameters), 0)

        
    def test_init_url(self):

        rc = client.RestClient(url=self.url, config=MinimalConfig)
        self.assertEqual(rc.url, self.url)

    def test_init_url_ipv4(self):

        rc = client.RestClient(url="https://192.168.1.1", config=MinimalConfig)
        self.assertEqual(rc.url, 'https://192.168.1.1')

    def test_init_url_ipv6(self):

        rc = client.RestClient(url="http://[2001:0db8:0a0b:12f0:0000:0000:0000:0001]", config=MinimalConfig)
        self.assertEqual(rc.url, 'http://[2001:0db8:0a0b:12f0:0000:0000:0000:0001]')
        rc = client.RestClient(url="http://[2001:db8:a0b:12f0::1]", config=MinimalConfig)
        self.assertEqual(rc.url, 'http://[2001:db8:a0b:12f0::1]')

    def test_init_url_host(self):

        rc = client.RestClient(url="http://localhost", config=MinimalConfig)
        self.assertEqual(rc.url, 'http://localhost')

    @unittest.expectedFailure
    def test_init_url_fail_no_scheme(self):

        client.RestClient(url="example.com")

    @unittest.expectedFailure
    def test_init_url_fail_invalid_scheme(self):

        client.RestClient(url="ftp://example.com")

    @unittest.expectedFailure
    def test_init_url_fail_invalid_ipv4(self):

        client.RestClient(url="https://255.255.1")


