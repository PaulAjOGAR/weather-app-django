# WeatherApp

A simple Django app that fetches daily historical weather data from Open-Meteo, with a form to search by location and date range, a results table, and a CSV download endpoint.

## Prerequisites
- Python 3.10+ (recommended)
- pip
- (Optional) A virtual environment tool such as `venv`
- Internet access (the app calls Open-Meteo APIs)

This project targets Windows paths in examples, but it works on macOS/Linux too (adapt commands accordingly).

## Quick Start (Windows PowerShell)

1) Clone or open the project directory

2) Create and activate a virtual environment
- Create: `python -m venv .venv`
- Activate: `.\.venv\Scripts\Activate.ps1`

3) Install dependencies
- If you have a `requirements.txt`, run: `pip install -r requirements.txt`
- If not, install Django and requests directly:
  - `pip install "django>=5.0,<6.0" requests`

4) Apply database migrations
- `cd weatherapp`
- `python manage.py migrate`

5) Run the development server
- `python manage.py runserver`

6) Open the app in your browser
- App home: http://127.0.0.1:8000/
  - You will see the Daily Weather form.
  - Enter a location (e.g., "Berlin"), pick a start and end date, and submit.
- Admin (optional): http://127.0.0.1:8000/admin/
  - Create a superuser first if you want to log in: `python manage.py createsuperuser`

## How It’s Wired
- Root URLConf: `weatherapp\mysite\urls.py` includes `weatherarchive.urls` at root.
- App URLs: `weatherapp\weatherarchive\urls.py`
  - `/` -> `daily_data` view: renders the form and results at the same URL via GET.
  - `/download/` -> `download_daily_csv` view: returns a CSV of the last query (uses query params).
- Core views: `weatherapp\weatherarchive\views.py`
- Forms: `weatherapp\weatherarchive\forms.py` (WeatherDailyForm is used by daily_data)
- Template: `weatherapp\weatherarchive\templates\weatherarchive\results.html`

## Testing
- There are currently no substantive tests; a stub exists at `weatherapp\weatherarchive\tests.py`.
- You can still run Django’s test runner:
  - From `weatherapp` directory: `python manage.py test`

## Common Issues & Tips
- If you see an import/URL error: ensure you are using the updated URLs (`/` for form+results, `/download/` for CSV) and that the app is installed.
- If API calls fail: ensure you have internet access; the app uses Open-Meteo public APIs (no key required). Temporary external failures will surface as user-visible errors.
- Date validation: Start date must be on or before the end date; adjust the dates if you see validation errors.
- Timezone: The API uses `timezone=auto` for results.

## Development Commands (reference)
- Activate venv: `.\.venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt`
- Make migrations (if you add models): `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Run server: `python manage.py runserver`
- Create superuser: `python manage.py createsuperuser`
- Run tests: `python manage.py test`

## Project Structure (key parts)
- `weatherapp/manage.py` — Django entry point
- `weatherapp/mysite/` — Project settings and URL routing
- `weatherapp/weatherarchive/` — App with views, forms, templates, URLs
- `docs/` — Project tasks and improvement checklist

## License
This repository did not include a license. Add one if you plan to distribute it.