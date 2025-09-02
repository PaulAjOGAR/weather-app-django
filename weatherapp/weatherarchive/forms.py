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
            lat = cleaned_data.get('latitude')
            lon = cleaned_data.get('longitude')
            if lat is None or lon is None:
                self.add_error('latitude', 'Latitude and longitude are required.')
                self.add_error('longitude', 'Latitude and longitude are required.')



class WeatherDailyForm(forms.Form):
    location = forms.CharField(label="Location", max_length=100)
    # Allow selecting years from 1940 through the current year
    start_date = forms.DateField(
        label="Start Date",
        widget=forms.SelectDateWidget(years=range(1940, __import__('datetime').date.today().year + 1))
    )
    end_date = forms.DateField(
        label="End Date",
        widget=forms.SelectDateWidget(years=range(1940, __import__('datetime').date.today().year + 1))
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            # Enforce lower bound for historical data
            from datetime import date as _date
            min_start = _date(1940, 1, 1)
            if start_date < min_start:
                self.add_error("start_date", "Start date cannot be earlier than 1940-01-01.")
            if start_date > end_date:
                self.add_error("end_date", "End date must be after start date.")

        return cleaned_data


class WeatherHourlyForm(WeatherDailyForm):
    """Reuse same fields/validation for hourly queries."""
    pass