# forms.py
from django import forms

from theanalystsplayground.dashboard.models import Portfolio


class PortfolioForm(forms.ModelForm):
    MARKET_TYPE_CHOICES = [
        ("stocks", "stocks"),
        ("crypto", "crypto"),
        ("fx", "forex"),
    ]

    market_type = forms.ChoiceField(
        choices=MARKET_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial="stocks",
        label="Market Type",
    )

    class Meta:
        model = Portfolio
        fields = ["ticker", "shares_owned", "price_per_unit", "market_type"]
        labels = {
            "ticker": "Ticker",
            "shares_owned": "How many shares?",
            "price_per_unit": "Price Per Share",
            "market_type": "Market Type",
        }


class PortfolioEditForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["ticker", "company_name", "shares_owned", "price_per_unit"]

        labels = {
            "ticker": "",
            "company_name": "",
            "shares_owned": "How many Shares?",
            "price_per_unit": "Price Per Share",
        }
