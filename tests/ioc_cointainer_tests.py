from django.test import TestCase
from reports.configuration.ioc_cointainer import get_file_storage_service, get_swapi_client


class IocContainerTest(TestCase):

    def test_objects_are_singletons(self):
        swapi_client1 = get_swapi_client()
        swapi_client2 = get_swapi_client()
        storage_service = get_file_storage_service()

        self.assertEqual(swapi_client2, swapi_client1)
        self.assertEqual(storage_service, swapi_client1.csv_storage_service)
