import unittest
import bcs_rest_client as client
import copy

#from bcs_rest_client.resources import validate_resources_configuration as v
from bcs_rest_client.conf import RESTConfig, EndPointConfig, BodyParameter, QueryParameter,  ParameterConfig
from bcs_rest_client.exception import BCSRestConfigurationError, BCSRestQueryError
from bcs_rest_client import RestClient


class TestQuickMarkerRepository(unittest.TestCase):
    url = "https://glent-test-1.be.bayercropscience/markerrepo/services/rest/v1"
    user = "bnlit005"
    password = "fubauoka"
    test_marker = 'mBRS00000001'
    
    class ConfigTest(RESTConfig):
        get_a_marker_by_id = EndPointConfig(path=["markers", "{id}"],  # {} means it's a path parameter
                                            method="GET")
        get_markers_by_criteria = EndPointConfig(
            path=["markers"],
            method="GET",
            parameters={'markerUid': QueryParameter(name="markerUid"),
                        'taxonId': QueryParameter(name="taxonId", multiple=True),
                        'alias': QueryParameter(name="alias"),
                        'sourceCategory': QueryParameter(name="sourceCategory"),
                        'technology': QueryParameter(name="technology"),
                        'page': QueryParameter(name="page"),
                        'size': QueryParameter(name="size"),
                        'sort': QueryParameter(name="sort", multiple=True)
                        }, 
            json = {"root": ["_embedded"]}
        )
        
    config = ConfigTest
    
    def setUp(self):
        self.mrep = client.RestClient(url=self.url, user=self.user, password=self.password, config=self.config)
    
    def test_get_nokeyword(self):
        with self.assertRaises(BCSRestQueryError) as e:
            response = self.mrep.get_a_marker_by_id(self.test_marker)

    def test_get_empty(self):
        with self.assertRaises(BCSRestQueryError) as e:
            response = self.mrep.get_a_marker_by_id()

    def test_get_mTO100(self):
        response = self.mrep.get_a_marker_by_id(id=self.test_marker)
        x = 1

    def test_get_badparameter(self):
        expected = "parameters ['id'] are supplied but not usable for resource 'get_markers_by_criteria'"
        with self.assertRaises(BCSRestQueryError) as e:
            response = self.mrep.get_markers_by_criteria(id=self.test_marker)
            x = 1

    def test_get_markerUid(self):
        response = self.mrep.get_markers_by_criteria(markerUid=self.test_marker)


class TestParameterConfig(unittest.TestCase):
    
    def run_param_set(self, **params):
        try:
            x =  ParameterConfig(**params)
        except BCSRestConfigurationError:
            return True
        else:
            return False
    
    def test_required_bool(self):
        para = {'name': 'name','required': 'yes',}
        if not self.run_param_set(**para):
            raise Exception('required allows non-boolean')

    def test_multiple_bool(self):
        para = {'name': 'name','multiple': 'yes',}
        if not self.run_param_set(**para):
            raise Exception('multiple allows non-boolean')
    
    def test_exclusion_group_string(self):
        para = {'name': 'name','exclusion_group': 42,}
        if not self.run_param_set(**para):
            raise Exception('exclusion_group allows non-string')

    def test_exclusion_group_nonprintable(self):
        para = {'name': 'name','exclusion_group': '\r\n',}
        if not self.run_param_set(**para):
            raise Exception('exclusion_group allows empty')
    

class TestEndPointConfig(unittest.TestCase):
    
    def setUp(self):
        self.endpointconf = {'path': ['root'], 'method': 'GET',}
        

    def parse_config_ok(self):
        '''
        running this should not yield problems
        '''
        test = EndPointConfig(**self.endpointconf)
        
    def parse_config_error(self, expected_response):
        try:
            test = EndPointConfig(**self.endpointconf)
        except BCSRestConfigurationError as e:
            self.assertEqual(str(e), expected_response)
        else:
            raise Exception('No Exception was raised')

    def test_path(self):
        self.endpointconf['path'] = None
        r = "path is not a list"
        self.parse_config_error(r)

    def test_path_parts_are_string(self):
        self.endpointconf['path'] = {'some_resource': {'path':['x', '{data}', ]}}
        r = "path is not a list"
        self.parse_config_error(r)

    def test_method(self):
        self.endpointconf['method'] = None
        r = "method must be GET or POST"
        self.parse_config_error(r)

    def test_query_parameters(self):
        self.endpointconf['parameters'] = 'yes'
        r = "parameters must be dictionary"
        self.parse_config_error(r)

    def test_query_parameters_empty(self):
        self.endpointconf['parameters'] = []
        self.parse_config_ok()

    def test_query_parameters_list(self):
        self.endpointconf['parameters'] = ['yes']
        r = "parameters must be dictionary"
        self.parse_config_error(r)

    def test_query_parameters_multiple(self):
        self.endpointconf['parameters'] = {'name': "test",}
        r = "Parameter 'name' must be ParameterConfig instance"
        self.parse_config_error(r)

    def test_query_parameters_json_number(self):
        self.endpointconf['json'] = 1
        r = "json option is not a dictionary"
        self.parse_config_error(r)

    def test_query_parameters_json_root_number(self):
        self.endpointconf['json'] = {'root': 1,}
        r = "json.root option is not a list"
        self.parse_config_error(r)

    def test_query_parameters_json_root_list_no(self):
        self.endpointconf['json'] = {'root': [1, 2, 3],}
        r = "json.source_name option is not a string"
        self.parse_config_ok()

    def test_query_parameters_json_source_name(self):
        self.endpointconf['json'] = {'source_name': [1, 2, 3],}
        r = "json.source_name option is not a string"
        self.parse_config_error(r)

    def test_query_parameters_json_result_name(self):
        self.endpointconf['json'] = {'source_name': [1, 2, 3],}
        r = "json.source_name option is not a string"
        self.parse_config_error(r)

    def test_query_parameters_header(self):
        self.endpointconf['headers'] = 'ok'
        r = "header is not a dict"
        self.parse_config_error(r)


class TestRestConfig(unittest.TestCase):

    def setUp(self):
        self.restconfig = {'url': 'http://www.example.com',}
        
    def parse_config_ok(self):
        '''
        running this should not yield problems
        '''
        test = RestClient(**self.restconfig)
    
    def parse_config_error(self, expected_response):
        try:
            test = RestClient(**self.restconfig)
        except BCSRestConfigurationError as e:
            self.assertEqual(str(e), expected_response)

    def test_badconfig1(self):
        self.restconfig['config'] = 'noclass'
        r = 'configuration is not a class'
        self.parse_config_error(r)

    def test_badconfig2(self):
        self.restconfig['config'] = dict
        r = 'configuration is not a RESTConfig'
        self.parse_config_error(r)

    def test_apply_default1(self):
        class ConfigTest(RESTConfig):
            default = 3
            ep1 = EndPointConfig([], 'GET')
        self.restconfig['config'] = ConfigTest
        r = 'default must be a dictionary'
        self.parse_config_error(r)

    def test_apply_default2(self):
        class ConfigTest(RESTConfig):
            default = {'a': 'b',}
            ep1 = EndPointConfig([], 'GET')
        self.restconfig['config'] = ConfigTest
        r = 'default config may only contain headers, json'
        self.parse_config_error(r)

    def test_apply_default_ok1(self):
        class ConfigTest(RESTConfig):
            default = {'headers': {'key': 'val',},
                       'json': {'root': ['blah'],},
                       }
            ep1 = EndPointConfig([], 'GET')
        self.restconfig['config'] = ConfigTest
        r = 'default config may only contain headers, json'
        self.parse_config_error(r)

    def test_apply_default_ok2(self):
        class ConfigTest(RESTConfig):
            default = {'headers': {'key': 'val',},
                       'json': {'root': ['blah'],},
                       }
            ep1 = EndPointConfig([], 'GET', headers={'k': 'v',}, json={'k': 'v',})
        self.restconfig['config'] = ConfigTest
        r = 'default config may only contain headers, json'
        self.parse_config_error(r)

    def test_return_class(self):
        class ConfigTest(RESTConfig):
            ep1 = EndPointConfig([], 'GET', return_class='blah')
        
        self.restconfig['config'] = ConfigTest
        r = 'unable to parse blah into module and class name' 
        self.parse_config_error(r)

    def test_return_class_ok(self):
        class ConfigTest(RESTConfig):
            ep1 = EndPointConfig([], 'GET', return_class='bcs_rest_client.resources.RestResource')
        self.restconfig['config'] = ConfigTest
        self.parse_config_ok()

    def test_endpoints1(self):
        class ConfigTest(RESTConfig):
            ep1 = dict()
        self.restconfig['config'] = ConfigTest
        r = 'no endpoints defined for this resource at all!' 
        self.parse_config_error(r)

    def test_endpoints2(self):
        class ConfigTest(RESTConfig):
            ep1 = EndPointConfig([], 'GET', return_class='bcs_rest_client.resources.RestResource')
            data = EndPointConfig([], 'GET', return_class='bcs_rest_client.resources.RestResource')
            
        self.restconfig['config'] = ConfigTest
        r = "resource name may not be named 'data'"
        self.parse_config_error(r)

        
class TestRestClientConfig(unittest.TestCase):

    def setUp(self):
        self.restconfig = {'url': 'http://www.example.com',}
        
    def parse_config_ok(self):
        '''
        running this should not yield problems
        '''
        test = RestClient(**self.restconfig)
    
    def parse_config_error(self, expected_response):
        try:
            test = RestClient(**self.restconfig)
        except BCSRestConfigurationError as e:
            self.assertEqual(str(e), expected_response)
        except:
            x = 1
            raise
        else:
            raise Exception()
    
    def test_invalid_url(self):
        self.restconfig['url'] = 'yes'
        r = 'Invalid URL specified.'
        self.parse_config_error(r)

    def test_invalid_url_ok(self):
        self.parse_config_ok()
        
        
