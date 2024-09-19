from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from theanalystsplayground.dashboard.dBoardHelpers.helper_functions import get_totals
from theanalystsplayground.dashboard.dBoardHelpers.helper_functions import (
    portfolio_data_injector,
)
from theanalystsplayground.dashboard.dBoardHelpers.helper_functions import (
    watchlist_data_injector,
)
from theanalystsplayground.dashboard.forms import PortfolioEditForm
from theanalystsplayground.dashboard.forms import PortfolioForm
from theanalystsplayground.dashboard.models import Portfolio
from theanalystsplayground.dashboard.models import Watchlist
from theanalystsplayground.Search.models import StocksData
from theanalystsplayground.Search.models import StockSearch

User = get_user_model()

##################################
# PORTFOLIO OPERATIONS
###############################


# delete things from Portfolio
@login_required
def htmx_portfolio_item_delete(request, ticker_id=None, mtype=None):
    context = {}
    context["user_id"] = request.user.username

    user = User.objects.get(username=request.user.username)
    Portfolio.objects.get(
        ticker=ticker_id.upper(),
        market_type=mtype,
        user=user,
    ).delete()
    model_instance = Portfolio.objects.filter(user=user)
    if model_instance:
        context["Portfolio"] = portfolio_data_injector(model_instance=model_instance)
        total = get_totals(context=context)
        if total:
            context["totalGainLoss"] = sum(total)
        else:
            context["totalGainLoss"] = None
    else:
        context["totalGainLoss"] = None

    return HttpResponse(
        render_to_string(
            "reusables/portfolioPlaceholder.html",
            context,
        ),
    )


# edit things in your Portfolio
@login_required
def htmx_edit_portfolio(request):
    context = {}
    context["user_id"] = request.user.username
    user = User.objects.get(username=request.user.username)
    form = PortfolioEditForm(request.POST)
    if form.is_valid():
        try:
            model_instance = Portfolio.objects.get(
                ticker=request.POST.get("ticker").upper(),
                company_name=request.POST.get("company_name"),
                user=user,
            )
        except Portfolio.DoesNotExist:
            return HttpResponseBadRequest("Not in Portfolio, sorry")

        model_instance.shares_owned = float(request.POST.get("shares_owned"))
        model_instance.price_per_unit = float(request.POST.get("price_per_unit"))
        model_instance.save()
        user_portfolio = Portfolio.objects.filter(user=user)
        context["Portfolio"] = portfolio_data_injector(user_portfolio)
        total = get_totals(context=context)
        if total:
            context["totalGainLoss"] = sum(total)

        else:
            context["totalGainLoss"] = None
        return HttpResponse(
            render_to_string(
                "reusables/portfolioPlaceholder.html",
                context,
            ),
        )

    return HttpResponseBadRequest("Please check your inputs")


# adding things to Portfolio
@login_required
def htmx_portfolio_swap(request):
    context = {}
    context["user_id"] = request.user.username
    user = User.objects.get(username=request.user.username)
    form = PortfolioForm(request.POST)
    if form.is_valid():
        ticker = request.POST.get("ticker")
        market_type = request.POST.get("market_type")
        # Check for existence in database
        ticker_info_additonal = StockSearch.objects.filter(
            public_ticker=ticker.upper(),
            market_type=market_type,
        )
        if not ticker_info_additonal.exists():
            return HttpResponseBadRequest(
                f"Sorry cant find {ticker.upper()}/{market_type}",
            )
        # check if in Portfolio
        precheck = Portfolio.objects.filter(
            ticker=ticker.upper(),
            market_type=market_type,
            user=user,
        )
        if precheck.exists():
            return HttpResponseBadRequest(
                f"{ticker.upper()} is already in your Portfolio",
            )

        # (StocksData db has better company names than
        # StockSearch db so im checking in
        # StocksData if it exists first if not the use
        # company names from StockSearch Database)
        if all(
            [
                ticker_info_additonal.first().market_type != "crypto",
                ticker_info_additonal.first().market_type != "fx",
            ],
        ):
            ticker_info = StocksData.objects.filter(ticker=ticker.upper())
            if not ticker_info.exists():
                ticker_info = ticker_info_additonal
        else:
            ticker_info = ticker_info_additonal

        model_instance = form.save(commit=False)
        model_instance.ticker = request.POST["ticker"].upper()
        model_instance.user = user
        model_instance.company_name = ticker_info.first().company_name
        model_instance.api_call_symbol = ticker_info_additonal.first().api_call_symbol
        model_instance.market_type = ticker_info_additonal.first().market_type
        model_instance.save()
        # RELOADING THE PORTFOLIO
        user_portfolio = Portfolio.objects.filter(user=user)
        context["Portfolio"] = portfolio_data_injector(model_instance=user_portfolio)
        total = get_totals(context)
        if total:
            context["totalGainLoss"] = sum(total)
        else:
            context["totalGainLoss"] = None
        return HttpResponse(
            render_to_string(
                "reusables/portfolioPlaceholder.html",
                context,
            ),
        )
    return HttpResponse(status=405)


########################################
# WATCHLIST OPERATIONS
#########################################
@login_required
def htmx_swap_delete(request, ticker_id=None, mtype=None):
    user = User.objects.get(username=request.user.username)
    Watchlist.objects.get(
        ticker=ticker_id.upper(),
        user=user,
        market_type=mtype,
    ).delete()
    context = {}
    user_watchlist = Watchlist.objects.filter(user=user)
    if user_watchlist.exists():
        context["allData"] = watchlist_data_injector(model_instance=user_watchlist)
        context["user_watchlist"] = True
    else:
        context["user_watchlist"] = None

    return HttpResponse(
        render_to_string(
            "reusables/watchlistPlaceholder.html",
            context,
        ),
    )


# WHEN THERE IS MULTILE TICKERS ARE MATCHED FOR WATCHLIST AND
# WATCHLIST IS SWITCHED OUT WITH CHOICES TO CHOoSE/
# IF THEY HIT THE X ICON THEN RELOAD THE WATCHLIST
@login_required
def htmx_reload(request):
    context = {}
    user = User.objects.get(username=request.user.username)
    user_watchlist = Watchlist.objects.filter(user=user)
    if user_watchlist.exists():
        context["user_watchlist"] = True
        context["allData"] = watchlist_data_injector(user_watchlist)

    else:
        context["user_watchlist"] = None

    return HttpResponse(
        render_to_string(
            "reusables/watchlistPlaceholder.html",
            context,
        ),
    )


def multipe_watchlist_match(request, mtype=None, ticker_id=None):
    user = User.objects.get(username=request.user.username)
    #    HANDLES LINKS FOR MULTIPLE MATCHES
    # if request.method == "GET":
    context = {}
    precheck = Watchlist.objects.filter(
        ticker=ticker_id.upper(),
        market_type=mtype,
        user=user,
    )
    # RETURN IF IN WATCHLIST
    if precheck.exists():
        return HttpResponseBadRequest(
            f"{precheck.first().ticker} already in watchlist!!",
        )

    # IF ITS NOT IN THE WATCHLIST ADD TO WATCHLIST THEN RELOAD THE WATCHLIST
    ticker_clicked = StockSearch.objects.filter(
        public_ticker=ticker_id,
        market_type=mtype,
    ).first()
    Watchlist.objects.create(
        ticker=ticker_clicked.public_ticker,
        company_name=ticker_clicked.company_name,
        api_call_symbol=ticker_clicked.api_call_symbol,
        market_type=ticker_clicked.market_type,
        user=user,
    )

    user_watchlist = Watchlist.objects.filter(user=user)
    if user_watchlist.exists():
        context["user_watchlist"] = True
        context["allData"] = watchlist_data_injector(model_instance=user_watchlist)
    else:
        context["user_watchlist"] = None

    # RETURN IF ADDED TO WATCHLIST
    return HttpResponse(
        render_to_string(
            "reusables/watchlistPlaceholder.html",
            context,
        ),
    )


@login_required
def htmx_swap_function(request, mtype=None, ticker_id=None):
    user = User.objects.get(username=request.user.username)
    if request.POST.get("stockBox"):
        context = {}
        ticker = request.POST.get("stockBox")
        pre_precheck = StockSearch.objects.filter(public_ticker=ticker.upper())
        precheck = Watchlist.objects.filter(ticker=ticker.upper(), user=user)
        if precheck.exists() and len(pre_precheck) == 1:
            return HttpResponseBadRequest(
                f"{precheck.first().ticker} is already in your watchlist!! ",
            )
        ticker_info = StockSearch.objects.filter(public_ticker=ticker.upper())
        #    IF THERE ARE MULTIPLE TICKERS IN DATABASE
        if len(ticker_info) > 1:
            context = {
                "q": ticker_info,
            }
            return HttpResponse(
                render_to_string("reusables/multiWatchlistMatches.html", context),
            )
            # IF THE TICKER DOES NOT EXISTS IN DATABASE
        if not ticker_info.exists():
            return HttpResponseBadRequest(f"Sorry can't find {ticker.upper()}!")

        # IF THERES ONE TICKER IN DATABASE AND ITS NOT ALREADY IN THE WATCHLIST

        query_info = ticker_info.first()
        company_name = query_info.company_name
        api_call_symbol = query_info.api_call_symbol
        market_type = query_info.market_type

        Watchlist.objects.create(
            ticker=ticker.upper(),
            company_name=company_name,
            api_call_symbol=api_call_symbol,
            market_type=market_type,
            user=user,
        )
        # RE RENDERING PAGE INFORMATION
        user_watchlist = Watchlist.objects.filter(user=user)
        if user_watchlist.exists():
            context["user_watchlist"] = True
            context["allData"] = watchlist_data_injector(
                model_instance=user_watchlist,
            )

        else:
            context["user_watchlist"] = None

        return HttpResponse(
            render_to_string(
                "reusables/watchlistPlaceholder.html",
                context,
            ),
        )

    # IF THEY HIT ENTER AND ITS EMPTY
    return HttpResponseBadRequest("NEED TO SPECIFY A TICKER")


#####################################
# DASHBOARD OPERATIONS
###################################


@login_required
def dashboard_dispatch_for_redirect(request, user_id=None):
    # FOR WHEN USER LOGINS IN THIS ATTACHES USER ID TO THE URL
    # FUNCTION IS CONNECTED TO THE SETTINGS.PY LOGIN_REDIRECT_URL
    return redirect(
        reverse(
            "dashboard_app:dashboard_view",
            kwargs={"user_id": request.user.username},
        ),
    )


@login_required
def dashboard_view(request, user_id=None):
    context = {}
    context["user_id"] = request.user.username
    pform = PortfolioForm()
    context["form"] = pform
    context["editForm"] = PortfolioEditForm()
    user = User.objects.get(username=request.user.username)
    user_watchlist = Watchlist.objects.filter(user=user)
    user_portfolio = Portfolio.objects.filter(user=user)
    if user_watchlist.exists():
        context["user_watchlist"] = True
        context["allData"] = watchlist_data_injector(model_instance=user_watchlist)
        watchlist_data_check = filter(
            lambda x: x is not None,
            [data.get("data") for ticker, data in context["allData"].items()],
        )
        context["watchlist_bad_request"] = not list(watchlist_data_check)

    else:
        context["user_watchlist"] = None
    if user_portfolio.exists():
        context["user_portfolio"] = True
        context["Portfolio"] = portfolio_data_injector(model_instance=user_portfolio)
        portfolio_data_check = filter(
            lambda x: x is not None,
            [data.get("data") for ticker, data in context["Portfolio"].items()],
        )
        if not list(portfolio_data_check):
            context["portfolio_bad_request"] = True
        else:
            context["portfolio_bad_request"] = False
        total = get_totals(context)

        if total:
            context["totalGainLoss"] = sum(total)

        else:
            context["totalGainLoss"] = None
            context["hasData"] = True
            # ADDED THIS FOR TEMPLATE DISPAYING;

            # (IF THERES DATA BUT CANT MAKE CALCULATIONS
            # I WANT TO DISPLAY UNABLE TO MAKE CALCULATIONS)
            # IF THERES NO DATA THEN I WANT TO DISPLAY ADD STOCKS TO PORTFOLIO
            # SEE DASHBOARD.HTML FOR MORE INFO
    else:
        context["Portfolio"] = None
        context["hasData"] = False

    return render(request, "dashboard/dashboard.html", context)


# username jellybean
# password !A2BcdefgH
# email jellybean@bean.com

# username badguy
# password !A2BcdefgH
# email throntonbill343@gmail.com
