import sqlite3
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from theanalystsplayground.Search.models import StockSearch

# Create your views here.


def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def dbloader_view(request):
    return render(request, "dbloader/load_db.html", {})


@login_required
@user_passes_test(is_staff)
def dbloader_forex_view(request):
    # ALREADY FINISHED!!!!!!!
    parent_path = Path(__file__).resolve(strict=True).parent
    db_path = parent_path / "forex.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    data = cur.execute("SELECT * FROM forex").fetchall()
    pre_check = StockSearch.objects.filter(market_type="fx")
    if not pre_check.exists():
        for (
            public_ticker,
            company_name,
            currency,
            currency_name,
            base_currency,
            base_currency_name,
            market_type,
            security_type,
            api_call_symbol,
        ) in data:
            obj, created = StockSearch.objects.get_or_create(
                public_ticker=public_ticker,
                defaults={
                    "company_name": company_name,
                    "currency": currency,
                    "currency_name": currency_name,
                    "base_currency": base_currency,
                    "base_currency_name": base_currency_name,
                    "market_type": market_type,
                    "security_type": security_type,
                    "api_call_symbol": api_call_symbol,
                },
            )

    return render(request, "dbloader/forex_finish.html", {})


@login_required
@user_passes_test(is_staff)
def dbloader_stocks_view(request):
    # ALREADY FINISHED!!!!
    parent_path = Path(__file__).resolve(strict=True).parent
    db_path = parent_path / "stocks.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    data = cur.execute("SELECT * FROM stocks").fetchall()
    pre_check = StockSearch.objects.filter(market_type="stocks")
    if not pre_check.exists():
        for (
            public_ticker,
            company_name,
            currency,
            currency_name,
            base_currency,
            base_currency_name,
            market_type,
            security_type,
            api_call_symbol,
        ) in data:
            obj, created = StockSearch.objects.get_or_create(
                company_name=company_name,
                defaults={
                    "public_ticker": public_ticker,
                    "currency": currency,
                    "currency_name": currency_name,
                    "base_currency": base_currency,
                    "base_currency_name": base_currency_name,
                    "market_type": market_type,
                    "security_type": security_type,
                    "api_call_symbol": api_call_symbol,
                },
            )
    return render(request, "dbloader/stocks_finish.html", {})


@login_required
@user_passes_test(is_staff)
def dbloader_crypto_view(request):
    # ALREADY FINISHED !!!
    parent_path = Path(__file__).resolve(strict=True).parent
    db_path = parent_path / "crypto.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    data = cur.execute("SELECT * FROM cryptoTable").fetchall()
    pre_check = StockSearch.objects.filter(market_type="crypto")
    if not pre_check.exists():
        for (
            public_ticker,
            company_name,
            currency,
            currency_name,
            base_currency,
            base_currency_name,
            market_type,
            security_type,
            api_call_symbol,
        ) in data:
            obj, created = StockSearch.objects.get_or_create(
                company_name=company_name,
                defaults={
                    "public_ticker": public_ticker,
                    "currency": currency,
                    "currency_name": currency_name,
                    "base_currency": base_currency,
                    "base_currency_name": base_currency_name,
                    "market_type": market_type,
                    "security_type": security_type,
                    "api_call_symbol": api_call_symbol,
                },
            )
    return render(request, "dbloader/crypto_finish.html", {})


@login_required
@user_passes_test(is_staff)
def dbloader_index_view(request):
    max_length = 10
    parent_path = Path(__file__).resolve(strict=True).parent
    db_path = parent_path / "index.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    data = cur.execute("SELECT * FROM indices").fetchall()
    pre_check = StockSearch.objects.filter(market_type="indices")
    if not pre_check.exists():
        for (
            public_ticker,
            company_name,
            currency,
            currency_name,
            base_currency,
            base_currency_name,
            market_type,
            security_type,
            api_call_symbol,
        ) in data:
            if len(api_call_symbol) <= max_length:
                obj, created = StockSearch.objects.get_or_create(
                    company_name=company_name,
                    defaults={
                        "public_ticker": public_ticker,
                        "currency": currency,
                        "currency_name": currency_name,
                        "base_currency": base_currency,
                        "base_currency_name": base_currency_name,
                        "market_type": market_type,
                        "security_type": security_type,
                        "api_call_symbol": api_call_symbol,
                    },
                )
    return render(request, "dbloader/index_finish.html", {})
