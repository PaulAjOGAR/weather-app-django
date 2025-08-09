"""from multiprocessing.managers import view_type"""

from django.shortcuts import render
from .forms import LocationForm

# Create your views here.

def location_search(request):
    form = LocationForm(request.POST or None)
    if request.method== 'POST' and form.is_valid():
        choice = form.cleaned_data['input']
        city = form.cleaned_data.get('city')
        postcode = form.cleaned_data.get('postcode')
        latitude = form.cleaned_data.get('latitude')
        longitude = form.cleaned_data.get('longitude')

        return render(request, 'weatherarchive/results.html',{
            'choice': choice,
            'city': city,
            'postcode': postcode,
            'latitude': latitude,
            'longitude': longitude,
        })
    return render(request,'weatherarchive/location_search.html', {'form': form})

