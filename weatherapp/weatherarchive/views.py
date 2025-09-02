import csv
import io
from datetime import date
from django.http import HttpResponse
from django.shortcuts import render
from .forms import WeatherDailyForm, WeatherHourlyForm, ContactForm
from .services.open_meteo import geocode as svc_geocode, fetch_daily as svc_fetch_daily, fetch_hourly as svc_fetch_hourly
from .utils.analysis import compute_stats, detect_anomalies
from django.conf import settings
from django.core.mail import EmailMessage


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
        tmean_api = daily.get("temperature_2m_mean") or []
        rh_mean = daily.get("relative_humidity_2m_mean") or []
        precip = daily.get("precipitation_sum") or []
        wind_max = daily.get("windspeed_10m_max") or []
        wind_mean = daily.get("windspeed_10m_mean") or []

        # Fallback for mean temperature if API mean not provided
        tmean = tmean_api if (tmean_api and len(tmean_api) == len(tmax) == len(tmin)) else [
            (mx + mn) / 2 if mx is not None and mn is not None else None for mx, mn in zip(tmax, tmin)
        ]

        # Basic stats and anomaly flags (z-score) for parity with Streamlit analysis
        tmax_stats = compute_stats(tmax)
        tmin_stats = compute_stats(tmin)
        tmean_stats = compute_stats(tmean)
        precip_stats = compute_stats(precip)
        wind_stats = compute_stats(wind_max)
        rh_stats = compute_stats(rh_mean)
        tmean_anoms = detect_anomalies(tmean)

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
            "tmean": tmean,
            "rh_mean": rh_mean,
            "precip": precip,
            "wind_max": wind_max,
            "wind_mean": wind_mean,
            "tmean_flags": tmean_anoms,
            # raw for table loop + anomaly flag per row
            "rows": list(zip(dates, tmax, tmin, tmean, rh_mean, precip, wind_max, tmean_anoms)),
            # stats
            "stats": {
                "tmax": tmax_stats,
                "tmin": tmin_stats,
                "tmean": tmean_stats,
                "precip": precip_stats,
                "wind": wind_stats,
                "rh": rh_stats,
            },
        })

    return render(request, "weatherarchive/results.html", context)


def home(request):
    return render(request, "weatherarchive/home.html", {})


def contact(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Honeypot check (if present)
            if hasattr(form, 'cleaned_data') and form.cleaned_data.get('honeypot'):
                form = ContactForm()  # reset form
            else:
                name = form.cleaned_data.get("name", "Anonymous")
                sender_email = form.cleaned_data.get("email", "")
                message_text = form.cleaned_data.get("message", "")
                subject = f"Website contact from {name}"
                body = f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_text}"
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_RECIPIENT_EMAIL],
                    reply_to=[sender_email] if sender_email else None
                )
                email.send(fail_silently=False)
                success = True
                form = ContactForm()  # reset form
    else:
        form = ContactForm()
    return render(request, "weatherarchive/contact.html", {"form": form, "success": success})


from .models import Testimonial
from django.shortcuts import redirect


def testimonials(request):
    success = False
    if request.method == "POST":
        from .forms import TestimonialForm
        form = TestimonialForm(request.POST)
        if form.is_valid():
            Testimonial.objects.create(
                name=form.cleaned_data["name"],
                role=form.cleaned_data.get("role", ""),
                rating=form.cleaned_data["rating"],
                message=form.cleaned_data["message"],
            )
            return redirect("weatherarchive:testimonials")
    else:
        form = None
    items = Testimonial.objects.all()[:25]
    if form is None:
        from .forms import TestimonialForm
        form = TestimonialForm()
    return render(request, "weatherarchive/testimonials.html", {"testimonials": list(items), "form": form, "success": success})


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
        cloud = hourly.get("cloudcover") or []
        pressure = hourly.get("surface_pressure") or []

        temp_stats = compute_stats(temp)
        rh_stats = compute_stats(rh)
        precip_stats = compute_stats(precip)
        wind_stats = compute_stats(wind)
        cloud_stats = compute_stats(cloud)
        pressure_stats = compute_stats(pressure)
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
            "cloud": cloud,
            "pressure": pressure,
            "temp_flags": temp_anoms,
            "rows": list(zip(times, temp, rh, precip, wind, cloud, pressure, temp_anoms)),
            "stats": {
                "temp": temp_stats,
                "rh": rh_stats,
                "precip": precip_stats,
                "wind": wind_stats,
                "cloud": cloud_stats,
                "pressure": pressure_stats,
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
    tmean_api = daily.get("temperature_2m_mean") or []
    tmean = tmean_api if (tmean_api and len(tmean_api) == len(tmax) == len(tmin)) else [
        (mx + mn) / 2 if mx is not None and mn is not None else None for mx, mn in zip(tmax, tmin)
    ]
    rh_mean = daily.get("relative_humidity_2m_mean") or []
    precip = daily.get("precipitation_sum") or []
    wind_max = daily.get("windspeed_10m_max") or []
    wind_mean = daily.get("windspeed_10m_mean") or []

    # Build CSV in-memory
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "temp_max_c", "temp_min_c", "temp_mean_c", "rh_mean_pct", "precip_mm", "wind_max_kmh", "wind_mean_kmh"])
    for row in zip(dates, tmax, tmin, tmean, rh_mean, precip, wind_max, wind_mean):
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
    cloud = hourly.get("cloudcover") or []
    pressure = hourly.get("surface_pressure") or []

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["time", "temp_c", "rh_pct", "precip_mm", "wind_kmh", "cloud_pct", "pressure_hpa"])
    for row in zip(times, temp, rh, precip, wind, cloud, pressure):
        writer.writerow(row)

    resp = HttpResponse(buf.getvalue(), content_type="text/csv")
    fname = f"hourly_weather_{display_name.replace(' ', '_')}_{start}_to_{end}.csv"
    resp["Content-Disposition"] = f'attachment; filename="{fname}"'
    return resp
