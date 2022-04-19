import os

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from reports.configuration.ioc_cointainer import get_swapi_client, get_file_storage_service

view_columns = os.environ.get("SWAPI_VIEW_COLUMNS")


def index(request):
    file_storage_service = get_file_storage_service()
    all_reports = file_storage_service.get_all_files_metadata()
    context = {'swapi_reports': all_reports}
    return render(request, 'index.html', context)


async def fetch(request):
    swapi_client = get_swapi_client()
    await swapi_client.get_the_latest_report()
    return HttpResponseRedirect(reverse('index'))


def report_info(request, report_id):
    rows_count = int(request.GET.get('rows_count', '') or '10')

    file_storage_service = get_file_storage_service()
    csv_data = file_storage_service.get_csv_data(report_id, 1, rows_count)
    context = {'report_id': report_id, 'columns': csv_data['columns'],
               'rows': csv_data['rows'], 'rows_count': rows_count}
    return render(request, 'report.html', context)


def grouping_view(request, report_id):
    selected_column = request.GET.get('selected_column', '')
    grouped_columns_list = list(filter(None, request.GET.get('grouped_columns', '').split('|')))

    context = {'report_id': report_id, 'all_columns': view_columns.split(",")}

    if selected_column != '':
        if selected_column in grouped_columns_list:
            grouped_columns_list.remove(selected_column)
        else:
            grouped_columns_list.append(selected_column)

    if len(grouped_columns_list) > 0:
        file_storage_service = get_file_storage_service()
        rows = file_storage_service.get_grouped_result(report_id, grouped_columns_list)
        context['grouped_columns'] = "|".join(grouped_columns_list)
        grouped_columns_list.append('count')
        context['grouped_columns_list'] = grouped_columns_list
        context['rows'] = rows

    return render(request, 'grouping_view.html', context)

