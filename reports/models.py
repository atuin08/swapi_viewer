from django.db import models


class Reports(models.Model):
    guid = models.CharField(max_length=200)
    created_date = models.DateTimeField('date created')
    file_name = models.CharField(max_length=200)

    @staticmethod
    def get_all_reports():
        return Reports.objects.all()

    @staticmethod
    def get_report_by_uid(report_uid):
        return Reports.objects.get(guid=report_uid)
