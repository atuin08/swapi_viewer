from reports.services.csv_file_storage_service import CsvFileStorageService
from reports.services.swapi_client import SwapiClient

file_storage_service = None
swapi_client = None


def get_file_storage_service():
    global file_storage_service
    if file_storage_service is None:
        file_storage_service = CsvFileStorageService()
    return file_storage_service


def get_swapi_client():
    global swapi_client
    if swapi_client is None:
        swapi_client = SwapiClient(get_file_storage_service())
    return swapi_client
