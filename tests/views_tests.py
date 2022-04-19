import os
from unittest import mock

from django.test import TestCase, Client, AsyncClient
from django.utils import timezone

from reports.models import Reports


class FakeSwapiClient:
    async def get_the_latest_report(self):
        pass


class FakeStorageService:
    def get_csv_data(self, report_id, start_row, rows_count):
        return {'columns': ["name", "age"], 'rows': [["Tom", "23"], ["Frankie", "33"]]}

    def get_grouped_result(self, report_id, columns):
        return [["Frank", "45"], ["Ela", "56"]]


class CsvFileStorageServiceTest(TestCase):

    def test_index_page(self):
        Reports.objects.create(guid="test_guid1", created_date=timezone.now(), file_name="test_file1")
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("test_guid1" in str(response.content))
        self.assertTrue("test_file1" in str(response.content))

    @mock.patch('reports.views.get_swapi_client')
    async def test_fetching(self, get_swapi_client):
        get_swapi_client.return_value = FakeSwapiClient()

        c = AsyncClient()
        response = await c.post('/fetch/', {})
        print(response)
        self.assertEqual(response.status_code, 302)

    @mock.patch('reports.views.get_file_storage_service')
    def test_report_info(self, get_file_storage_service):
        get_file_storage_service.return_value = FakeStorageService()

        c = Client()
        response = c.get('/report/testid/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("testid" in str(response.content))
        self.assertTrue("Tom" in str(response.content))
        self.assertTrue("Frankie" in str(response.content))
        self.assertTrue("age" in str(response.content))

    @mock.patch('reports.views.get_file_storage_service')
    def test_report_rows_count(self, get_file_storage_service):
        c = Client()
        response = c.get('/report/testid/?rows_count=30')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("rows_count=40" in str(response.content))

    @mock.patch('reports.views.view_columns')
    @mock.patch('reports.views.get_file_storage_service')
    def test_grouping_view(self, get_file_storage_service, view_columns):
        get_file_storage_service.return_value = FakeStorageService()
        view_columns.return_value = "name,age"

        c = Client()
        response = c.get('/report/testid/grouping?grouped_columns=name|age')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("name" in str(response.content))
        self.assertTrue("age" in str(response.content))
        self.assertTrue("Frank" in str(response.content))
        self.assertTrue("Ela" in str(response.content))

    @mock.patch('reports.views.view_columns')
    @mock.patch('reports.views.get_file_storage_service')
    def test_grouping_view_select_column(self, get_file_storage_service, view_columns):
        get_file_storage_service.return_value = FakeStorageService()
        view_columns.return_value = "name,age,height"

        c = Client()
        response = c.get('/report/testid/grouping?grouped_columns=name|age&selected_column=height')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("name" in str(response.content))
        self.assertTrue("age" in str(response.content))
        self.assertTrue("height" in str(response.content))
        self.assertTrue("Ela" in str(response.content))
