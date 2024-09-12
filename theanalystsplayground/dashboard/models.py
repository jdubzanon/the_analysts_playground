from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.


class Watchlist(models.Model):
    ticker = models.CharField(default="", max_length=10)
    company_name = models.CharField(default="", max_length=500)
    api_call_symbol = models.CharField(default="", max_length=10)
    market_type = models.CharField(default="", max_length=25)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticker


class Portfolio(models.Model):
    ticker = models.CharField(default="", max_length=10)
    company_name = models.CharField(default="", max_length=250)
    api_call_symbol = models.CharField(default="", max_length=10)
    market_type = models.CharField(default="", max_length=10)
    shares_owned = models.FloatField(default="", validators=[MinValueValidator(0.0)])
    price_per_unit = models.FloatField(default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticker
