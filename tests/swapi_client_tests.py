from re import match
from unittest import mock

from django.test import TestCase

from reports.services.swapi_client import SwapiClient


class FakeStorageService:
    def save_responses_to_csv(self, responses, file_name, homeworld_map_function):
        pass


class FakeMockResponse:

    def __init__(self):
        self.text = '{ "count" : 11, "results": [] }'


class SwapiClientTest(TestCase):

    @mock.patch("reports.services.swapi_client.requests.get")
    async def test_get_the_latest_report(self, request_mock):
        request_mock.return_value = FakeMockResponse()
        swapi_client = SwapiClient(FakeStorageService())

        report = await swapi_client.get_the_latest_report()

        self.assertNotEqual(report, None)
        self.assertTrue(match(".*csv", report.file_name))

