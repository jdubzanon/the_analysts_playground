from django.shortcuts import render

from theanalystsplayground.HomePage.HomeFunctions.view_all_helper_functions import (
    get_api_info,
)
from theanalystsplayground.StockCenter.helperFunctions.helper_functions import (
    get_industry_drop_down_menu_options,
)
from theanalystsplayground.StockCenter.helperFunctions.helper_functions import (
    get_sector_api_data,
)
from theanalystsplayground.StockCenter.helperFunctions.helper_functions import (
    get_sector_drop_down_menu_options,
)


def stock_center_view(request, user_id=None):
    # Getting Industry choice
    industry_choice = request.GET.get("industry-dropdown")
    sector_choice = request.GET.get("sector-dropdown")
    industry_options = (
        get_industry_drop_down_menu_options()
    )  # <-- returns a list of all industries for dropdown menu
    sector_options = (
        get_sector_drop_down_menu_options()
    )  # <-- returns a list for dropdown menu
    if industry_choice:
        data = get_api_info(value=industry_choice)

    elif sector_choice:
        data = get_sector_api_data(value=sector_choice)

    else:
        data = None
    if data:
        status_check = filter(
            lambda x: x is not None,
            [
                each_data.get("data")
                for industry, info in data.items()
                for each_info, each_data in info.items()
            ],
        )
        all_request_failed = not list(status_check)
    else:
        all_request_failed = False
    context = {
        "IndustryOptions": industry_options,
        "SectorOptions": sector_options,
        "industry_choice": industry_choice,
        "data": data,
        "search_parameters": sector_choice if sector_choice else industry_choice,
        "all_request_failed": all_request_failed,
    }
    return render(request, "StockCenter/StockCenter.html", context)
