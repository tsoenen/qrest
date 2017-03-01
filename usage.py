import marker_repository
import uid_generator
import pprint

markerUrl = "https://glent-test-1.be.bayercropscience/markerrepo/services/rest/v1"
uidUrl = "https://example.com/uid"
user = "gfjom"  # or use something like os.getenv('MARKER_USER', 'default_value')
password = "Welkom1001"
pp = pprint.PrettyPrinter(indent=4)


def use_marker_repository_client():

    client = marker_repository.MarkerRepositoryClient(url=markerUrl,
                                                      user=user,
                                                      password=password)
    pp.pprint(client.resources())
    x = client.get_a_marker_by_id(id='mTO100')
    pp.pprint(x)


def use_uid_generator_client():

    client = uid_generator.UidGeneratorClient(url=uidUrl,
                                              user=user,
                                              password=password)
    pp.pprint(client.list_targets())


if __name__ == '__main__':
    use_marker_repository_client()
    #use_uid_generator_client()
