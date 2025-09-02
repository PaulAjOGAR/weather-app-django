from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "role", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("name", "role", "message")

# Register your models here.
