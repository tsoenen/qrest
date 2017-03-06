import unittest
import bcs_rest_client as client
import copy

from bcs_rest_client.resources import validate_resources_configuration as v


class TestQuickMarkerRepository(unittest.TestCase):
    url = "https://glent-test-1.be.bayercropscience/markerrepo/services/rest/v1"
    user = "bnlit005"
    password = "fubauoka"
    test_marker = 'mBRS00000001'

    config = {
        "get_a_marker_by_id": {
            "path": ["markers", "{id}"],  # {} means it's a path parameter
            "method": "GET",
        },
        "get_markers_by_criteria": {
            "path": ["markers"],
            "method": "GET",
            "query_parameters": [
                {"name": "markerUid"},
                {"name": "taxonId", "multiple": True},
                {"name": "alias"},
                {"name": "sourceCategory"},
                {"name": "technology"},
                {"name": "page"},
                {"name": "size"},
                {"name": "sort", "multiple": True}
            ],
            "json": {"root": ["_embedded"]}
        },
    }
    
    def setUp(self):
        self.mrep = client.RestClient(url=self.url, user=self.user, password=self.password, config=self.config)
    
    def test_get_nokeyword(self):
        with self.assertRaises(SyntaxError) as e:
            response = self.mrep.get_a_marker_by_id(self.test_marker)

    def test_get_empty(self):
        with self.assertRaises(SyntaxError) as e:
            response = self.mrep.get_a_marker_by_id()

    def test_get_mTO100(self):
        response = self.mrep.get_a_marker_by_id(id=self.test_marker)
        x = 1

    def test_get_badparameter(self):
        expected = "parameters ['id'] are supplied but not usable for resource 'get_markers_by_criteria'"
        with self.assertRaises(SyntaxError) as e:
            response = self.mrep.get_markers_by_criteria(id=self.test_marker)
            x = 1

    def test_get_markerUid(self):
        response = self.mrep.get_markers_by_criteria(markerUid=self.test_marker)


class TestConfig(unittest.TestCase):
    
    def parse_config(self, config_dict, ExpectedExceptionClass, expected_response):
        try:
            v(config_dict)
        except ExpectedExceptionClass as e:
            self.assertEqual(str(e), expected_response)
        else:
            raise Exception('No Exception was raised')

    def test_name(self):
        c = {1: 'x',}
        r = "resource name '1' is not a string"
        e = ValueError
        self.parse_config(c, e, r)

    def test_config_dict(self):
        c = {'some_resource': 'x',}
        r = "resource name 'some_resource' value is not a dictionary"
        e = ValueError
        self.parse_config(c, e, r)

    def test_path_list(self):
        c = {'some_resource': {'path':'notalist'},}
        r = "path for resource 'some_resource' is not a list"
        e = ValueError
        self.parse_config(c, e, r)

    def test_path_parts(self):
        c = {'some_resource': {'path':[1, 2, 3]}}
        
        r = "part '1' of path for resource 'some_resource' is not a string"
        e = ValueError
        self.parse_config(c, e, r)

    def test_path_data(self):
        c = {'some_resource': {'path':['x', '{data}', ]}}
        r = "'data' isn't a valid path parameter name for resource 'some_resource'"   
        e = SyntaxError
        self.parse_config(c, e, r)

    def test_method(self):
        c = {'some_resource': {'method':1}}
        r = "method for resource 'some_resource' is not a string"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters(self):
        c = {'some_resource': {'query_parameters':1}}
        r = "query parameters for resource 'some_resource' is not a list"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters_emptylist(self):
        c = {'some_resource': {'query_parameters':[]}}
        r = "query parameters for resource 'some_resource' is empty"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters_isdict(self):
        c = {'some_resource': {'query_parameters':[1, 2]}}
        r = "not all query parameters for resource 'some_resource' are a dictionary"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters_name(self):
        c = {'some_resource': {'query_parameters':[{}]}}
        r = "not all query parameters for resource 'some_resource' have a name"
        e = SyntaxError
        self.parse_config(c, e, r)

    def test_query_parameters_name_string(self):
        c = {'some_resource': {'query_parameters':[{'name': 1,}]}}
        r = "not all query parameter names for resource 'some_resource' are a string"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters_data(self):
        c = {'some_resource': {'query_parameters':[{'name': 'data',}]}}
        r = "'data' isn't a valid query parameter name for resource 'some_resource'" 
        e = SyntaxError
        self.parse_config(c, e, r)

    def test_query_parameters_group(self):
        c = {'some_resource': {'query_parameters':[{'name': 'my_name', 'group': 1,}]}}
        r = "not all query parameter group names for resource 'some_resource' are a string"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters_required(self):
        c = {'some_resource': {'query_parameters':[{'name': 'my_name', 'required': 'yes',}]}}
        r = "not all query parameter 'required' options for resource 'some_resource' are a boolean"
        e = ValueError
        self.parse_config(c, e, r)

    def test_query_parameters_multiple(self):
        c = {'some_resource': {'query_parameters':[{'name': 'my_name', 'multiple': 'yes',}]}}
        r = "not all query parameter 'multiple' options for resource 'some_resource' are a boolean"
        e = ValueError
        self.parse_config(c, e, r)

    def test_json_dict(self):
        c = {'some_resource': {'json': 1,}}
        r = "json option for resource 'some_resource' is not a dictionary"
        e = ValueError
        self.parse_config(c, e, r)

    def test_json_root_list(self):
        c = {'some_resource': {'json': {'root': 1,},}}
        r = "json.root option for resource 'some_resource' is not a list"
        e = ValueError
        self.parse_config(c, e, r)

    def test_json_root_list_string(self):
        c = {'some_resource': {'json': {'root': [1, 2, 3],},}}
        r = "json.root list element 1 for resource 'some_resource' is not a string" 
        e = ValueError
        self.parse_config(c, e, r)

    def test_json_source_name(self):
        c = {'some_resource': {'json': {'source_name': [1, 2, 3],},}}
        r = "json.source_name option for resource 'some_resource' is not a string"
        e = ValueError
        self.parse_config(c, e, r)

    def test_json_result_name(self):
        c = {'some_resource': {'json': {'result_name': [1, 2, 3],},}}
        r = "json.result_name option for resource 'some_resource' is not a string"
        e = ValueError
        self.parse_config(c, e, r)
        