import json
import math
from datetime import datetime

from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection
from .views2 import cursor_items_from_db, dates_to_str, date_validator

# Create your views here.


def z3_generate_query_get(bool_search_string, order_by, order_type, bool_last_update_gte, bool_last_update_lte):

    start = """
    
    SELECT co.cin, co.name, co.br_section, co.address_line, co.last_update, 
        Aggregation_opi.total as or_podanie_issues_count, 
        Aggregation_zii.total as znizenie_imania_issues_count,
        Aggregation_li.total as likvidator_issues_count, 
        Aggregation_kvi.total as konkurz_vyrovnanie_issues_count, 
        Aggregation_kra.total as konkurz_restrukturalizacia_actors_count
    FROM ov.companies co
    
    LEFT JOIN
    (
        SELECT company_id, count(company_id) as total
        FROM ov.or_podanie_issues
        GROUP BY company_id
    ) as Aggregation_opi
    ON Aggregation_opi.company_id = co.cin
    
    LEFT JOIN
    (
        SELECT company_id, count(company_id) as total
        FROM ov.znizenie_imania_issues
        GROUP BY company_id
    ) as Aggregation_zii
    ON Aggregation_zii.company_id = co.cin
    
    LEFT JOIN
    (
        SELECT company_id, count(company_id) as total
        FROM ov.likvidator_issues
        GROUP BY company_id
    ) as Aggregation_li
    ON Aggregation_li.company_id = co.cin
    
    LEFT JOIN
    (
        SELECT company_id, count(company_id) as total
        FROM ov.konkurz_vyrovnanie_issues
        GROUP BY company_id
    ) as Aggregation_kvi
    ON Aggregation_kvi.company_id = co.cin
    
    LEFT JOIN
    (
        SELECT company_id, count(company_id) as total
        FROM ov.konkurz_restrukturalizacia_actors
        GROUP BY company_id
    ) as Aggregation_kra
    ON Aggregation_kra.company_id = co.cin
            """

    where = """WHERE """
    if bool_search_string:
        where += """(name ILIKE %(search)s OR address_line ILIKE %(search)s)
                """
    else:
        where = """"""

    if bool_last_update_gte or bool_last_update_lte:
        if len(where) == 0:
            where = "WHERE "
        else:
            where += " AND "

        if bool_last_update_gte and bool_last_update_lte:
            where += "last_update >= %(reg_gte)s AND last_update <= %(reg_lte)s" + "\n"
        elif bool_last_update_gte:
            where += "last_update >= %(reg_gte)s" + "\n"
        else:
            where += "last_update <= %(reg_lte)s" + "\n"

    order = "ORDER BY " + order_by + " " + order_type + "\n"

    end = """LIMIT %(limit)s
            OFFSET %(offset)s;
        """

    query = start + where + order + end

    return query


def z3_generate_variables_get(limit, offset, bool_search_string, search,
                              bool_last_update_gte, reg_gte, bool_last_update_lte, reg_lte):

    variables = {"limit": limit, "offset": offset}

    if bool_search_string:
        variables["search"] = search

    if bool_last_update_gte:
        variables["reg_gte"] = reg_gte

    if bool_last_update_lte:
        variables["reg_lte"] = reg_lte

    return variables


def z3_generate_query_metadata(bool_search_string, bool_last_update_gte, bool_last_update_lte):

    start = """ SELECT COUNT(cin)
                FROM ov.companies
            """

    where = """WHERE """
    if bool_search_string:
        where += """(name ILIKE %(search)s OR address_line ILIKE %(search)s)
                """
    else:
        where = """"""

    if bool_last_update_gte or bool_last_update_lte:
        if len(where) == 0:
            where = "WHERE "
        else:
            where += " AND "

        if bool_last_update_gte and bool_last_update_lte:
            where += "last_update >= %(reg_gte)s AND last_update <= %(reg_lte)s" + "\n"
        elif bool_last_update_gte:
            where += "last_update >= %(reg_gte)s" + "\n"
        else:
            where += "last_update <= %(reg_lte)s" + "\n"

    query = start + where

    return query


def z3_generate_metadata(page, per_page, variables, bool_search_string, bool_last_update_gte, bool_last_update_lte):

    query = z3_generate_query_metadata(bool_search_string, bool_last_update_gte, bool_last_update_lte)

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        items = cursor.fetchall()

    try:
        all_items = items[0][0]
    except:
        all_items = 0

    pages = math.ceil(all_items / per_page)

    return {"page": page, "per_page": per_page, "pages": pages, "total": all_items}


def z3_get_print_pages(request):

    allParameters = request.GET

    page = allParameters.get('page', '1')
    try:
        page_int = int(page)
    except:
        page_int = 1

    per_page = allParameters.get('per_page', '10')
    try:
        per_page_int = int(per_page)
    except:
        per_page_int = 10

    search = allParameters.get('query')
    bool_search_string = False

    if search is not None:
        bool_search_string = True
        search = "%" + search + "%"

    last_update_gte = allParameters.get("last_update_gte")
    bool_last_update_gte = date_validator(last_update_gte)

    last_update_lte = allParameters.get("last_update_lte")
    bool_last_update_lte = date_validator(last_update_lte)

    collumn_names = ["cin", "name", "br_section", "address_line", "last_update", "or_podanie_issues_count",
                     "znizenie_imania_issues_count", "likvidator_issues_count", "konkurz_vyrovnanie_issues_count",
                     "konkurz_restrukturalizacia_actors_count"]
    possible_order_types = ["asc", "desc"]

    order_by = allParameters.get("order_by", "cin")
    order_by = order_by.lower()
    if order_by not in collumn_names:
        order_by = "cin"

    default_order_type = "desc"
    order_type = allParameters.get("order_type", default_order_type)
    order_type = order_type.lower()
    if order_type not in possible_order_types:
        order_type = default_order_type

    page_offset = (page_int - 1) * per_page_int

    query = z3_generate_query_get(bool_search_string, order_by, order_type, bool_last_update_gte, bool_last_update_lte)

    variables = z3_generate_variables_get(per_page_int, page_offset, bool_search_string, search,
                                          bool_last_update_gte, last_update_gte, bool_last_update_lte, last_update_lte)

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        items = cursor_items_from_db(cursor)

    items = dates_to_str(items, ["last_update"])

    metadata = z3_generate_metadata(page_int, per_page_int, variables, bool_search_string,
                                    bool_last_update_gte, bool_last_update_lte)

    result = {"items": items, "metadata": metadata}

    # print(bool_search_string, order_by, order_type, bool_last_update_gte, bool_last_update_lte)
    # print(variables)
    #
    # result = {"items": items}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response