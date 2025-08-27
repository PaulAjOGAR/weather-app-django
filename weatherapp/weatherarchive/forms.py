from django import forms

class LocationForm(forms.Form):
    input = forms.ChoiceField(
        choices=[
            ('city', 'City'),
            ('postcode', 'Postcode'),
            ('manual', 'ManualCoordinates')
        ],
        widget=forms.RadioSelect
    )
    city = forms.CharField(required=False)
    postcode = forms.CharField(required=False)
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        choice = cleaned_data.get('input')

        if choice == 'city' and not cleaned_data.get('city'):
            self.add_error('city', 'City name is required.')
        elif choice == 'postcode' and not cleaned_data.get('postcode'):
            self.add_error('postcode', 'Postcode is required.')
        elif choice == 'manual':
            if not cleaned_data.get('latitude') or not cleaned_data.get('longitude'):
                self.add_error('latitude', 'Latitude and longitude are required.')


class WeatherDailyForm:
