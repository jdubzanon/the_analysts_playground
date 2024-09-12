from django.db import models


# Create your models here.
class StockSearch(models.Model):
    public_ticker = models.CharField(default="", max_length=10)
    company_name = models.CharField(default="", max_length=500)
    currency = models.CharField(default="", max_length=50)
    currency_name = models.CharField(default="", max_length=100)
    base_currency = models.CharField(default="", max_length=25)
    base_currency_name = models.CharField(default="", max_length=100)
    market_type = models.CharField(default="", max_length=25)
    security_type = models.CharField(default="", max_length=25)
    api_call_symbol = models.CharField(default="", max_length=25)

    class Meta:
        app_label = "Search"

    def __str__(self):
        return self.public_ticker


class StocksData(models.Model):
    ticker = models.CharField(max_length=10)
    company_name = models.CharField(max_length=200)
    cik_str = models.PositiveIntegerField()
    sector = models.CharField(max_length=75)
    industry = models.CharField(max_length=200)
    market_cap = models.BigIntegerField()

    def __str__(self):
        return self.ticker
