from django.db import models


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.rating}/5)"


class LocationCache(models.Model):
    name = models.CharField(max_length=200)
    admin1 = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'admin1', 'country_code')
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.name}, {self.admin1}, {self.country_code} ({self.latitude}, {self.longitude})"
