import marker_repository
import uid_generator
import pprint

markerUrl = "https://example.com/markerrepo"
uidUrl = "https://example.com/uid"
user = ""  # or use something like os.getenv('MARKER_USER', 'default_value')
password = ""
pp = pprint.PrettyPrinter(indent=4)


def use_marker_repository_client():

    client = marker_repository.MarkerRepositoryClient(url=markerUrl,
                                                      user=user,
                                                      password=password)
    pp.pprint(client.list_targets())


def use_uid_generator_client():

    client = uid_generator.UidGeneratorClient(url=uidUrl,
                                              user=user,
                                              password=password)
    pp.pprint(client.list_targets())


if __name__ == '__main__':
    use_marker_repository_client()
    use_uid_generator_client()
