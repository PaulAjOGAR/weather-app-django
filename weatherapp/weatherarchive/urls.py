from django.urls import path
from . import views

app_name = 'weatherarchive'

urlpatterns = [
    path('', views.daily_data, name='daily_data'),
    path('download/', views.download_daily_csv, name='download_daily_csv'),
]