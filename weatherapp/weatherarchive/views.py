import csv
import io
from datetime import date
from django.http import HttpResponse
from django.shortcuts import render
from .forms import WeatherDailyForm, WeatherHourlyForm
from .services.open_meteo import geocode as svc_geocode, fetch_daily as svc_fetch_daily, fetch_hourly as svc_fetch_hourly
from .utils.analysis import compute_stats, detect_anomalies


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

        lat, lon, display_name = svc_geocode(location)
        if lat is None:
            context["error"] = "Could not find that location. Try a different name."
            return render(request, "weatherarchive/results.html", context)

        data = svc_fetch_daily(lat, lon, start, end)

        # Guard for missing data
        daily = data.get("daily") or {}
        dates = daily.get("time") or []
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        precip = daily.get("precipitation_sum") or []
        wind = daily.get("windspeed_10m_max") or []

        # Basic stats and anomaly flags (z-score) for parity with Streamlit analysis
        tmax_stats = compute_stats(tmax)
        tmin_stats = compute_stats(tmin)
        precip_stats = compute_stats(precip)
        wind_stats = compute_stats(wind)
        tmax_anoms = detect_anomalies(tmax)

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
            # raw for table loop + anomaly flag per row
            "rows": list(zip(dates, tmax, tmin, precip, wind, tmax_anoms)),
            # stats
            "stats": {
                "tmax": tmax_stats,
                "tmin": tmin_stats,
                "precip": precip_stats,
                "wind": wind_stats,
            },
        })

    return render(request, "weatherarchive/results.html", context)


def hourly_data(request):
    """
    Renders the Hourly Data page similar to daily, but with hourly variables.
    """
    form = WeatherHourlyForm(request.GET or None)
    context = {"form": form, "has_results": False}

    if form.is_valid():
        location = form.cleaned_data["location"]
        start = form.cleaned_data["start_date"]
        end = form.cleaned_data["end_date"]

        lat, lon, display_name = svc_geocode(location)
        if lat is None:
            context["error"] = "Could not find that location. Try a different name."
            return render(request, "weatherarchive/hourly_results.html", context)

        data = svc_fetch_hourly(lat, lon, start, end)
        hourly = data.get("hourly") or {}
        times = hourly.get("time") or []
        temp = hourly.get("temperature_2m") or []
        rh = hourly.get("relative_humidity_2m") or []
        precip = hourly.get("precipitation") or []
        wind = hourly.get("windspeed_10m") or []

        temp_stats = compute_stats(temp)
        rh_stats = compute_stats(rh)
        precip_stats = compute_stats(precip)
        wind_stats = compute_stats(wind)
        temp_anoms = detect_anomalies(temp)

        context.update({
            "has_results": True,
            "display_name": display_name,
            "lat": lat,
            "lon": lon,
            "start": start,
            "end": end,
            "times": times,
            "temp": temp,
            "rh": rh,
            "precip": precip,
            "wind": wind,
            "rows": list(zip(times, temp, rh, precip, wind, temp_anoms)),
            "stats": {
                "temp": temp_stats,
                "rh": rh_stats,
                "precip": precip_stats,
                "wind": wind_stats,
            },
        })

    return render(request, "weatherarchive/hourly_results.html", context)


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

    lat, lon, display_name = svc_geocode(location)
    if lat is None:
        return HttpResponse("Location not found.", status=404)

    data = svc_fetch_daily(lat, lon, date.fromisoformat(start), date.fromisoformat(end))
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


def download_hourly_csv(request):
    """CSV download for hourly results."""
    location = request.GET.get("location")
    start = request.GET.get("start_date")
    end = request.GET.get("end_date")

    if not (location and start and end):
        return HttpResponse("Missing query parameters.", status=400)

    lat, lon, display_name = svc_geocode(location)
    if lat is None:
        return HttpResponse("Location not found.", status=404)

    data = svc_fetch_hourly(lat, lon, date.fromisoformat(start), date.fromisoformat(end))
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    temp = hourly.get("temperature_2m") or []
    rh = hourly.get("relative_humidity_2m") or []
    precip = hourly.get("precipitation") or []
    wind = hourly.get("windspeed_10m") or []

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["time", "temp_c", "rh_pct", "precip_mm", "wind_kmh"])
    for row in zip(times, temp, rh, precip, wind):
        writer.writerow(row)

    resp = HttpResponse(buf.getvalue(), content_type="text/csv")
    fname = f"hourly_weather_{display_name.replace(' ', '_')}_{start}_to_{end}.csv"
    resp["Content-Disposition"] = f'attachment; filename="{fname}"'
    return resp
