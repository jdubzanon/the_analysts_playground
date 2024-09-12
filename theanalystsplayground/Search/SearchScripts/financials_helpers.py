def get_financial_values(keychoices=None, data_frame=None, special_cases_key=None):
    if special_cases_key:
        passing_list = list(data_frame.loc[special_cases_key][0:4])
    else:
        generic_key = ""
        for key in keychoices:
            if key in data_frame.index:
                generic_key = key
                break
        if generic_key:
            passing_list = list(data_frame.loc[generic_key][0:4])
        else:
            passing_list = ["N/A" for _ in range(4)]
    return passing_list


def balance_sheet_processor(balance_sheet):
    # BALANCE SHEET METRICS BEGIN
    bs_map = {}
    # BALANCE SHEET CURRENT ASSETS HANDLER
    current_asset_keys = [
        "Current Assets",
        "Cash Cash Equivalents And Short Term Investments",
        "Cash And Cash Equivalents",
    ]
    current_asset_key = ""
    for key in current_asset_keys:
        if key in balance_sheet.index:
            current_asset_key = key
            break
    if current_asset_key:
        bs_map[current_asset_key] = get_financial_values(
            special_cases_key=current_asset_key,
            data_frame=balance_sheet,
        )
    else:  # <-- if not key matches the return a list of n/a
        bs_map["Current Assets"] = get_financial_values(
            keychoices=current_asset_keys,
            data_frame=balance_sheet,
        )

    # BALANCE SHEET TOTAL ASSET HANDLER
    total_asset_keys = ["Total Assets"]
    bs_map["Total Assets"] = get_financial_values(
        keychoices=total_asset_keys,
        data_frame=balance_sheet,
    )

    # BALANCE SHEET CURRENT LIABILTIES HANDLER
    current_liabilities_keys = [
        "Current Liabilities",
        "Current Debt And Capital Lease Obligation",
        "Current Debt",
    ]
    bs_map["Current Liabilities"] = get_financial_values(
        keychoices=current_liabilities_keys,
        data_frame=balance_sheet,
    )

    total_liabilities_keys = [
        "Total Liabilities",
        "Total Liabilities Net Minority Interest",
    ]
    bs_map["Total Liabilities"] = get_financial_values(
        keychoices=total_liabilities_keys,
        data_frame=balance_sheet,
    )

    retain_earning_keys = ["Retained Earnings"]
    bs_map["Retained Earnings"] = get_financial_values(
        keychoices=retain_earning_keys,
        data_frame=balance_sheet,
    )

    stockholders_equity_keys = ["Stockholders Equity", "Common Stock Equity"]
    bs_map["Stockholder Equity"] = get_financial_values(
        keychoices=stockholders_equity_keys,
        data_frame=balance_sheet,
    )
    return bs_map


def income_statement_processor(income_statement):
    # INCOME STATEMENT METRICS BEGINS
    income_map = {}
    total_revenue_keys = ["Total Revenue", "Operating Revenue"]
    income_map["Total Revenue"] = get_financial_values(
        keychoices=total_revenue_keys,
        data_frame=income_statement,
    )

    operating_expense_keys = ["Operating Expense"]
    opex_key = ""
    for key in operating_expense_keys:
        if key in income_statement.index:
            opex_key = key
            break
    if opex_key:
        income_map["Operating Expense"] = get_financial_values(
            special_cases_key=opex_key,
            data_frame=income_statement,
        )

    gross_profit_keys = ["Gross Profit", "Pretax Income"]
    income_map["Gross Profit"] = get_financial_values(
        keychoices=gross_profit_keys,
        data_frame=income_statement,
    )

    total_expense_keys = ["Total Expenses", "Tax Provision"]
    additional_expense_key = ""
    for key in total_expense_keys:
        if key in income_statement.index:
            additional_expense_key = key
            break
    if additional_expense_key:
        income_map[additional_expense_key] = get_financial_values(
            special_cases_key=additional_expense_key,
            data_frame=income_statement,
        )
    else:
        income_map["Total Expenses"] = get_financial_values(
            keychoices=total_expense_keys,
            data_frame=income_statement,
        )

    net_income_keys = [
        "Net Income",
        "Net Income From Continuing And Discontinued Operation",
        "Net Income Continuous Operations",
    ]
    income_map["Net Income"] = get_financial_values(
        keychoices=net_income_keys,
        data_frame=income_statement,
    )

    eps_keys = ["Diluted EPS", "Basic EPS"]
    income_map["EPS"] = get_financial_values(
        keychoices=eps_keys,
        data_frame=income_statement,
    )
    return income_map


def cashflow_statement_processor(cf_statement):
    # CASHFLOW STATEMENT BEGINS
    cash_flow_map = {}
    net_income_from_opex_keys = ["Net Income From Continuing Operations"]
    cash_flow_map["Income From Operations"] = get_financial_values(
        keychoices=net_income_from_opex_keys,
        data_frame=cf_statement,
    )

    cash_flow_from_operations_keys = ["Cash Flow From Continuing Operating Activities"]
    cash_flow_map["Cashflow From Operations"] = get_financial_values(
        keychoices=cash_flow_from_operations_keys,
        data_frame=cf_statement,
    )

    cash_flow_from_financing_keys = ["Cash Flow From Continuing Financing Activities"]
    cash_flow_map["Cashflow From Financing"] = get_financial_values(
        keychoices=cash_flow_from_financing_keys,
        data_frame=cf_statement,
    )

    cash_flow_from_investing_keys = ["Cash Flow From Continuing Investing Activities"]
    cash_flow_map["Cashflow From Investing"] = get_financial_values(
        keychoices=cash_flow_from_investing_keys,
        data_frame=cf_statement,
    )

    changes_in_cash_keys = ["Changes In Cash"]
    cash_flow_map["Changes In Cash"] = get_financial_values(
        keychoices=changes_in_cash_keys,
        data_frame=cf_statement,
    )

    free_cashflow_keys = ["Free Cash Flow"]
    cash_flow_map["Free Cash Flow"] = get_financial_values(
        keychoices=free_cashflow_keys,
        data_frame=cf_statement,
    )
    return cash_flow_map
