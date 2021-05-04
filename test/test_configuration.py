import unittest

from typing import Dict

from qrest import APIConfig, RestClientConfigurationError
from qrest import QueryParameter, BodyParameter, FileParameter, ResourceConfig
from qrest import JSONResource
from qrest.auth import UserPassAuthConfig


def _create_endpoints(**kwargs) -> Dict[str, ResourceConfig]:
    """Return endpoints for testing purposes.

    This function creates a single ResourceConfig for path ``[""]``, method
    ``GET`` and the keyword arguments from its signature. The endpoint is named
    ``ep``.

    """
    return {"ep": ResourceConfig(path=[""], method="GET", **kwargs)}


class TestMinimal(unittest.TestCase):
    def test_minimal_config(self):
        """
        check method or path
        """

        class Config(APIConfig):
            url = "http://localhost"

        Config({"ep": ResourceConfig(path=[""], method="GET")})

        Config({"ep": ResourceConfig(path=["test"], method="GET")})

        with self.assertRaises(RestClientConfigurationError):

            Config({"ep": ResourceConfig(path=["test"], method="ERR")})

        with self.assertRaises(RestClientConfigurationError):

            Config({"ep": ResourceConfig(path=3, method="GET")})

        with self.assertRaises(RestClientConfigurationError):

            Config({"ep": ResourceConfig(path=[""], method="ERR")})


class TestParameters(unittest.TestCase):
    def setUp(self):
        class UrlApiConfig(APIConfig):
            url = "http://localhost"

        self.UrlApiConfig = UrlApiConfig

    def test_good_query_parameters(self):
        parameters = {
            "para": QueryParameter(name="sort",
                                   default="some_default",
                                   description="description",
                                   example='foobar')
        }
        self.UrlApiConfig(_create_endpoints(parameters=parameters))

        parameters = {"para": QueryParameter(name="sort", required=False)}
        self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_bad_query_parameters(self):
        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", required=3)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", multiple=3)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", exclusion_group=3)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name=None)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        with self.assertRaises(RestClientConfigurationError):

            parameters = {
                "para": QueryParameter(name="sort", default="some_default", required=True)
            }
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_exclusion_group(self):
        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", exclusion_group="\n")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", default="x", choices=["a", "b"])}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_choices(self):
        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", choices="some_default")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_descriptions(self):
        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": QueryParameter(name="sort", description=3)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_good_example_with_choices(self):
        parameters = {"para": QueryParameter(name="sort",
                                             example=3,
                                             choices=[1, 2, 3])}
        self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_bad_example_with_choices(self):
        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": QueryParameter(name="sort",
                                                 example=3,
                                                 choices=[1, 2, 4])}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        self.assertEqual(exc.exception.args[0], "example should be one of the choices")

    def test_schema_with_choices(self):
        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": QueryParameter(name="sort",
                                                 schema={'type': 'string'},
                                                 choices=[1, 2, 4])}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        self.assertEqual(exc.exception.args[0], "choices and schema can't be combined")

    def test_bad_body_parameters(self):
        with self.assertRaises(RestClientConfigurationError):

            parameters = {"para": BodyParameter(name="sort")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

    def test_bad_file_parameters(self):
        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": FileParameter(name="sort", default="c")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        msg = "parameter 'default' should be 'None' for FileParameter"
        self.assertEqual(exc.exception.args[0], msg)

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": FileParameter(name="test", example=3)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        msg = "parameter 'example' should be 'None' for FileParameter"
        self.assertEqual(exc.exception.args[0], msg)

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": FileParameter(name="test", schema={'type': 'string'})}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        msg = "parameter 'schema' should be 'None' for FileParameter"
        self.assertEqual(exc.exception.args[0], msg)

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": FileParameter(name=None)}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        msg = "parameter 'name' can't be 'None' for FileParameter"
        self.assertEqual(exc.exception.args[0], msg)

    def test_good_schema_parameters(self):
        parameters = {"para": BodyParameter(name="foo",
                                            schema={'type': 'boolean'},
                                            example=True)}

        self.UrlApiConfig({"ep": ResourceConfig(path=[""],
                                                method="POST",
                                                parameters=parameters)})

        parameters = {"para": QueryParameter(name="foo",
                                             schema={'type': 'integer'},
                                             default=4)}

        self.UrlApiConfig({"ep": ResourceConfig(path=[""],
                                                method="POST",
                                                parameters=parameters)})

    def test_bad_schema_parameters(self):

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": BodyParameter(name="foo",
                                                schema="bar")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        self.assertEqual(exc.exception.args[0], "parameter schema must be dict")

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": QueryParameter(name="foo",
                                                 schema={'type': 'ni'},
                                                 example="bar")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        self.assertEqual(exc.exception.args[0], "provided schema is not a valid schema")

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": BodyParameter(name="foo",
                                                schema={'type': 'boolean'},
                                                example="bar")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        self.assertEqual(exc.exception.args[0], "example does not obey schema")

        with self.assertRaises(RestClientConfigurationError) as exc:

            parameters = {"para": QueryParameter(name="foo",
                                                 schema={'type': 'boolean'},
                                                 default="bar")}
            self.UrlApiConfig(_create_endpoints(parameters=parameters))

        self.assertEqual(exc.exception.args[0], "default does not obey schema")


class TestEndpoint(unittest.TestCase):
    def setUp(self):
        class UrlApiConfig(APIConfig):
            url = "http://localhost"

        self.UrlApiConfig = UrlApiConfig

    def test_bad_init_parameters(self):
        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(description=3))

        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(path_description=3))

        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(headers="none"))

    def test_no_endpoints(self):
        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig({})

    def test_bad_rest_parameters(self):
        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(parameters="x"))

        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(parameters={"x": "y"}))

    def test_bad_endpoints(self):
        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig({"data": ResourceConfig(path=[""], method="GET")})

    def test_bad_defaults(self):
        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                default_headers = "error"

            Config(_create_endpoints())

        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                default_headers = ({"key": 3},)

            Config(_create_endpoints())

        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                default_headers = ({"key": None},)

            Config(_create_endpoints())

    def test_good_defaults(self):
        class Config(self.UrlApiConfig):
            default_headers = {"key": "val"}

        Config(_create_endpoints())

        config = Config(_create_endpoints(headers={"key": "oldval"}))
        self.assertDictEqual(config.endpoints["ep"].headers, {"key": "oldval"})

        class Config(self.UrlApiConfig):
            ep = ResourceConfig(path=[""], method="GET", headers={"otherkey": "val"})
            default_headers = {"key": "val"}

        config = Config(_create_endpoints(headers={"otherkey": "val"}))
        self.assertDictEqual(config.endpoints["ep"].headers, {"key": "val", "otherkey": "val"})

    def test_descriptions(self):
        self.UrlApiConfig(_create_endpoints(description="OK"))

        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(description=3))

        self.UrlApiConfig(_create_endpoints(path_description={"x": "y"}))

        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(path_description=3))

    def test_introspection(self):
        endpoints = {
            "ep1": ResourceConfig(
                path=[""],
                method="GET",
                parameters={
                    "p1": QueryParameter("p1"),
                    "p2": QueryParameter("p2", multiple=True),
                    "p3": QueryParameter("p3", required=True),
                    "p4": QueryParameter("p4", default="def"),
                },
            )
        }

        c = self.UrlApiConfig(endpoints)
        expected = {"required": ["p3"], "optional": ["p1", "p2", "p4"], "multiple": ["p2"]}

        ep1_endpoint = c.endpoints["ep1"]
        self.assertDictEqual(ep1_endpoint.query_parameters, expected)

        self.assertListEqual(ep1_endpoint.all_query_parameters, ["p1", "p2", "p4", "p3"])
        self.assertListEqual(ep1_endpoint.required_parameters, ["p3"])
        self.assertListEqual(ep1_endpoint.multiple_parameters, ["p2"])
        self.assertListEqual(ep1_endpoint.all_parameters, ["p1", "p2", "p4", "p3"])

        self.assertDictEqual(
            ep1_endpoint.as_dict, {"required": ["p3"], "optional": ["p1", "p2", "p4"]}
        )
        self.assertDictEqual(ep1_endpoint.defaults, {"p4": "def"})

        endpoints = {
            "ep1": ResourceConfig(
                path=[""],
                method="GET",
                parameters={
                    "p1": QueryParameter("p1"),
                    "p2": QueryParameter("p2", multiple=True, exclusion_group="a"),
                    "p3": QueryParameter("p3", required=True, exclusion_group="a"),
                    "p4": QueryParameter("p4"),
                },
            )
        }
        c = self.UrlApiConfig(endpoints)

        expected = {"a": ["p2", "p3"]}
        ep1_endpoint = c.endpoints["ep1"]
        self.assertDictEqual(ep1_endpoint.query_parameter_groups, expected)

        endpoints = {"ep1": ResourceConfig(path=["x", "y", "z"], method="GET")}
        c = self.UrlApiConfig(endpoints)

        expected = []
        ep1_endpoint = c.endpoints["ep1"]
        self.assertListEqual(expected, ep1_endpoint.path_parameters)

        endpoints = {"ep1": ResourceConfig(path=["x", "{y}", "z"], method="GET")}
        c = self.UrlApiConfig(endpoints)

        expected = ["y"]
        ep1_endpoint = c.endpoints["ep1"]
        self.assertListEqual(expected, ep1_endpoint.path_parameters)


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        class UrlApiConfig(APIConfig):
            url = "http://localhost"

        self.UrlApiConfig = UrlApiConfig

    def test_bad_auth(self):
        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                authentication = 4

            Config(_create_endpoints())

    def test_not_init_auth(self):
        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                authentication = UserPassAuthConfig

            Config(_create_endpoints())

    def test_good_auth(self):
        class Config(self.UrlApiConfig):
            authentication = UserPassAuthConfig()

        Config(_create_endpoints())


class TestMainConfiguration(unittest.TestCase):
    def setUp(self):
        class UrlApiConfig(APIConfig):
            pass

        self.UrlApiConfig = UrlApiConfig

    def test_bad_verify_ssl(self):
        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                url = "http://localhost"
                verify_ssl = 3

            Config(_create_endpoints())

    def test_good_verify_ssl(self):
        class Config(self.UrlApiConfig):
            url = "http://localhost"
            verify_ssl = True

        Config(_create_endpoints())

    def test_bad_server(self):
        with self.assertRaises(RestClientConfigurationError):

            class Config(self.UrlApiConfig):
                url = "http://badserver"

            Config(_create_endpoints())

    def test_good_server(self):
        endpoints = _create_endpoints()

        class Config(self.UrlApiConfig):
            url = "http://localhost"

        Config(endpoints)

        class Config(self.UrlApiConfig):
            url = "http://server.tld"

        Config(endpoints)

        class Config(self.UrlApiConfig):
            url = "http://server.tld:8080"

        Config(endpoints)


class TestResourceClass(unittest.TestCase):
    def setUp(self):
        class UrlApiConfig(APIConfig):
            url = "http://localhost"

        self.UrlApiConfig = UrlApiConfig

    def test_empty_processor(self):

        self.UrlApiConfig(_create_endpoints(processor=JSONResource()))

    def test_good_processor(self):
        self.UrlApiConfig(
            _create_endpoints(
                processor=JSONResource(extract_section=["a", "b", "c"], create_attribute="sink")
            )
        )

    def test_bad_processor(self):
        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(processor="error"))

        with self.assertRaises(RestClientConfigurationError):

            self.UrlApiConfig(_create_endpoints(processor=JSONResource))

        with self.assertRaises(TypeError):

            self.UrlApiConfig(_create_endpoints(processor=JSONResource("error")))
