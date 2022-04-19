import os
from unittest import mock

import petl
from django.test import TestCase
from django.utils import timezone

from reports.models import Reports
from reports.services.csv_file_storage_service import CsvFileStorageService


class CsvFileStorageServiceTest(TestCase):

    def test_get_all_files_metadata(self):
        Reports.objects.create(guid="test_guid1", created_date=timezone.now(), file_name="test_file1")
        Reports.objects.create(guid="test_guid2", created_date=timezone.now(), file_name="test_file2")

        service = CsvFileStorageService()

        all_files = service.get_all_files_metadata()

        self.assertEqual(len(all_files), 2)
        self.assertEqual(Reports.objects.get(guid="test_guid1").file_name, "test_file1")

    @mock.patch.dict(os.environ, {"SWAPI_COLUMNS": "name,age,mass,hair_color,skin_color,homeworld,edited"})
    @mock.patch('reports.services.csv_file_storage_service.petl.tocsv')
    def test_save_responses_to_csv(self, petl_to_csv_mock):
        test_response1 = [{"name": "Tom", "age": "25", "homeworld": "test"}, {"name": "Bob", "age": "52"}]
        test_response2 = [{"name": "Ed", "age": "90", "edited": "2014-12-20T21:17:50.311000Z"},
                          {"name": "Moe", "age": "77"}]

        service = CsvFileStorageService()

        modified_petl_table = None

        def mock_csv_save(table, file_name):
            nonlocal modified_petl_table
            modified_petl_table = table

        petl_to_csv_mock.side_effect = mock_csv_save

        service.save_responses_to_csv([test_response1, test_response2], "test_file", lambda x: x)

        self.assertTrue('date' in petl.header(modified_petl_table))
        self.assertEqual(petl.data(modified_petl_table)[0][0], "Tom")
        self.assertEqual(petl.data(modified_petl_table)[2][6], "2014-12-20")

    @mock.patch('reports.services.csv_file_storage_service.petl.fromcsv')
    def test_get_csv_data(self, petl_from_csv_mock):
        test_dicts = [{"name": "Tom", "age": "25", "homeworld": "test"}, {"name": "Bob", "age": "52"},
                      {"name": "Ed", "age": "90", "edited": "2014-12-20T21:17:50.311000Z"},
                      {"name": "Moe", "age": "77"}]

        Reports.objects.create(guid="random_uid", created_date=timezone.now(), file_name="random_file")

        petl_from_csv_mock.return_value = petl.fromdicts(test_dicts)

        service = CsvFileStorageService()
        result = service.get_csv_data("random_uid", 1, 0)
        self.assertEqual(len(result['rows']), 1)
        result = service.get_csv_data("random_uid", 1, 2)
        self.assertEqual(len(result['rows']), 3)

    @mock.patch('reports.services.csv_file_storage_service.petl.fromcsv')
    def test_get_grouped_result(self, petl_from_csv_mock):
        test_dicts = [{"name": "Tom", "age": "25", "homeworld": "test"}, {"name": "Bob", "age": "52"},
                      {"name": "Tom", "age": "90", "edited": "2014-12-20T21:17:50.311000Z"},
                      {"name": "Moe", "age": "25"}]

        Reports.objects.create(guid="random_uid", created_date=timezone.now(), file_name="random_file")

        petl_from_csv_mock.return_value = petl.fromdicts(test_dicts)

        service = CsvFileStorageService()
        result = service.get_grouped_result("random_uid", ["name"])
        self.assertEqual(len(result), 3)
        result = service.get_grouped_result("random_uid", ["age"])
        self.assertEqual(len(result), 3)
        result = service.get_grouped_result("random_uid", ["age", "name"])
        self.assertEqual(len(result), 4)
        result = service.get_grouped_result("random_uid", ["edited"])
        self.assertEqual(len(result), 2)
