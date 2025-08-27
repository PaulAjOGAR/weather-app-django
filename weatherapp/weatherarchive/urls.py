from django.urls import path
from . import views
"""from .. site.urls import urlpatterns"""

urlpatterns = [
    path('',views.location_search, name='location_search'),
]