import re

from django.contrib.postgres.search import SearchQuery


def process_index_search_string(company_name=None):
    search_strings = []
    start = 0
    split_company_name = company_name.split()
    for i in range(0, len(split_company_name), 2):
        if i > 0:
            search_strings.append(split_company_name[start:i])
            start = i
    if not search_strings:
        pattern = r"\b[a-zA-Z]\w*"
        search_strings = re.findall(pattern, company_name)
    return search_strings


def process_etf_string(company_name=None):
    pattern = r"\b[a-zA-Z]\w*"
    return re.findall(pattern, company_name)


def get_index_high(page_requested=None, index_high=None, big_switch=None):
    if page_requested == "nextPage":
        if big_switch:
            index_high += 50
        else:
            index_high += 5

    elif page_requested == "prevPage":
        if big_switch:
            index_high -= 50
        else:
            index_high -= 5

    return index_high


def get_index_low(page_requested=None, index_low=None, big_switch=None):
    if page_requested == "nextPage":
        if big_switch:
            index_low += 50
        else:
            index_low += 5

    elif page_requested == "prevPage":
        if big_switch:
            index_low -= 50
        else:
            index_low -= 5

    return index_low


def build_data_map(results=None):
    return {
        obj.api_call_symbol: {
            "ticker": obj.public_ticker,
            "indexName": obj.company_name,
            "market_type": obj.market_type,
            "security_type": obj.security_type,
            "data": None,
        }
        for obj in results
    }


def build_search_query(search_strings=None):
    search_queries = [SearchQuery(query) for query in search_strings]
    combined_queries = search_queries[0]
    for q in search_queries[1:]:
        combined_queries |= q
    return combined_queries
