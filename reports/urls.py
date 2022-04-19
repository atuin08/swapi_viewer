from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('report/<slug:report_id>/', views.report_info, name='report'),
    path('report/<slug:report_id>/grouping', views.grouping_view, name='grouping_view'),
    path('fetch/', views.fetch, name='fetch')
]
