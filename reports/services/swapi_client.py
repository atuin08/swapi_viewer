import json
import math
import os
import requests
import asyncio
from datetime import datetime

from asgiref.sync import sync_to_async
from django.utils import timezone
import uuid

from reports.models import Reports


class SwapiClient:

    def __init__(self, csv_storage_service):
        self.base_swapi_url = os.environ.get("SWAPI_BASE_URL")
        self.csv_storage_service = csv_storage_service

    async def get_the_latest_report(self):
        loop = asyncio.get_event_loop()
        futures = []
        for x in range(self._get_number_of_people_pages()):
            futures.append(loop.run_in_executor(None, self._get_people_data_for_page_number, x+1))

        responses = []
        for future in futures:
            response = await future
            responses.append(response)

        new_guid = uuid.uuid4().hex
        now = timezone.now()
        csv_file_name = f"{datetime.timestamp(now)}_{new_guid}.csv"

        homeworld_map_function = self._map_homeworld_to_name_with_cache()
        self.csv_storage_service.save_responses_to_csv(responses, csv_file_name, homeworld_map_function)

        report = Reports(guid=new_guid, file_name=csv_file_name, created_date=now)

        await sync_to_async(report.save, thread_sensitive=False)()
        return report

    def _map_homeworld_to_name_with_cache(self):
        cached_responses = {}

        def get_homeworld_name(endpoint):
            if endpoint in cached_responses:
                return cached_responses[endpoint]

            response = requests.get(endpoint)
            response_dict = json.loads(response.text)

            cached_responses[endpoint] = response_dict['name']
            return response_dict['name']

        return get_homeworld_name

    def _get_people_data_for_page_number(self, page_number):
        response = requests.get(f'{self.base_swapi_url}people?page={page_number}')
        response_dict = json.loads(response.text)
        return response_dict['results']

    def _get_number_of_people_pages(self):
        response = requests.get(f'{self.base_swapi_url}people')
        response_dict = json.loads(response.text)
        return math.ceil(int(response_dict['count']) / 10)
