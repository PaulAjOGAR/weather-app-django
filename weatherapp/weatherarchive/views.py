import csv
import io
from datetime import date
import requests
from django.http import HttpResponse
from django.shortcuts import render
from .forms import WeatherDailyForm


def _geocode(name: str):
    """Return (lat, lon, display_name) from Open-Meteo geocoding API or (None, None, None)."""
    try:
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": name, "count": 1},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            return None, None, None
        top = data["results"][0]
        display = f'{top.get("name")}, {top.get("country_code", "")}'.strip(", ")
        return top["latitude"], top["longitude"], display
    except Exception:
        return None, None, None


def _fetch_daily(lat: float, lon: float, start: date, end: date):
    """Fetch daily history from Open-Meteo Archive."""
    daily_params = ",".join([
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "windspeed_10m_max",
    ])
    r = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": daily_params,
            "timezone": "auto",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def daily_data(request):
    """
    Renders the Daily Data page:
    - shows form
    - if valid query: fetches data, prepares arrays for chart/table
    """
    form = WeatherDailyForm(request.GET or None)

    context = {"form": form, "has_results": False}

    if form.is_valid():
        location = form.cleaned_data["location"]
        start = form.cleaned_data["start_date"]
        end = form.cleaned_data["end_date"]

        lat, lon, display_name = _geocode(location)
        if lat is None:
            context["error"] = "Could not find that location. Try a different name."
            return render(request, "weatherarchive/results.html", context)

        data = _fetch_daily(lat, lon, start, end)

        # Guard for missing data
        daily = data.get("daily") or {}
        dates = daily.get("time") or []
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        precip = daily.get("precipitation_sum") or []
        wind = daily.get("windspeed_10m_max") or []

        context.update({
            "has_results": True,
            "display_name": display_name,
            "lat": lat,
            "lon": lon,
            "start": start,
            "end": end,
            # Arrays for Plotly in the template
            "dates": dates,
            "tmax": tmax,
            "tmin": tmin,
            "precip": precip,
            "wind": wind,
            # raw for table loop
            "rows": list(zip(dates, tmax, tmin, precip, wind)),
        })

    return render(request, "weatherarchive/results.html", context)


def download_daily_csv(request):
    """
    CSV download endpoint. Re-fetches the data using query params
    so users can download exactly what they just saw.
    """
    location = request.GET.get("location")
    start = request.GET.get("start_date")
    end = request.GET.get("end_date")

    if not (location and start and end):
        return HttpResponse("Missing query parameters.", status=400)

    lat, lon, display_name = _geocode(location)
    if lat is None:
        return HttpResponse("Location not found.", status=404)

    data = _fetch_daily(lat, lon, date.fromisoformat(start), date.fromisoformat(end))
    daily = data.get("daily") or {}
    dates = daily.get("time") or []
    tmax = daily.get("temperature_2m_max") or []
    tmin = daily.get("temperature_2m_min") or []
    precip = daily.get("precipitation_sum") or []
    wind = daily.get("windspeed_10m_max") or []

    # Build CSV in-memory
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "temp_max_c", "temp_min_c", "precip_mm", "wind_max_kmh"])
    for row in zip(dates, tmax, tmin, precip, wind):
        writer.writerow(row)

    resp = HttpResponse(buf.getvalue(), content_type="text/csv")
    fname = f"daily_weather_{display_name.replace(' ', '_')}_{start}_to_{end}.csv"
    resp["Content-Disposition"] = f'attachment; filename="{fname}"'
    return resp
