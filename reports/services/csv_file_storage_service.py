import os
from collections import OrderedDict
from datetime import datetime

from reports.models import Reports
import petl


class CsvFileStorageService:

    def __init__(self):
        self.view_columns = os.environ.get("SWAPI_COLUMNS")

    def get_all_files_metadata(self):
        return Reports.get_all_reports()

    def save_responses_to_csv(self, responses, file_name, homeworld_map_function):
        petl_table = None
        for response in responses:
            response_table = petl.fromdicts(response)
            if petl_table is None:
                petl_table = response_table
            else:
                petl_table = petl.cat(petl_table, response_table)

        table_filtered_columns = petl.cat(petl_table, header=self.view_columns.split(","))
        table_date_header_modified = petl.rename(table_filtered_columns, 'edited', 'date')
        date_formatted = petl.convert(table_date_header_modified, 'date',
                                      self._convert_date_from_swapi)

        homeworld_mapped = petl.convert(date_formatted, 'homeworld',
                                        homeworld_map_function)

        petl.tocsv(homeworld_mapped, f'data/{file_name}')

    def get_csv_data(self, report_uid, start_row_number, end_row_number):
        csv_table = self._load_csv_table_by_report_id(report_uid)
        data_only = petl.data(csv_table)
        result = petl.rowslice(data_only, start_row_number - 1, end_row_number - start_row_number + 1)

        return {'columns': petl.header(csv_table), 'rows': list(result)}

    def get_grouped_result(self, report_uid, columns_list):
        csv_table = self._load_csv_table_by_report_id(report_uid)
        aggregation = OrderedDict()
        aggregation['count'] = len

        if len(columns_list) == 1:
            aggregated_table = petl.aggregate(csv_table, columns_list[0], aggregation=aggregation)
        else:
            aggregated_table = petl.aggregate(csv_table, key=tuple(columns_list), aggregation=aggregation)

        return list(petl.data(aggregated_table))

    def _convert_date_from_swapi(self, input_str):
        return str(datetime.strptime(input_str, "%Y-%m-%dT%H:%M:%S.%fZ").date().isoformat())

    def _load_csv_table_by_report_id(self, report_uid):
        file_name = Reports.get_report_by_uid(report_uid).file_name
        return petl.fromcsv(f'data/{file_name}')
