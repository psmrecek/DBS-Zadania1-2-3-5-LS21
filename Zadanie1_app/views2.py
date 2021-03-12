import math

from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection


# Create your views here.


def url_dispatcher(request):

    method = request.method

    print(request.path)
    print(request.scheme)
    print(method)

    response = HttpResponse("")

    if method == 'GET':
        response = get_print_pages(request)
    elif method == 'POST':
        response = post_add_row(request)
    elif method == 'DELETE':
        response = delete_row(request)

    return response


def OLD_cursor_items_from_db(query, vars=None):

    with connection.cursor() as cursor:
        cursor.execute(query, vars)
        columns = [col[0] for col in cursor.description]
        items = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        return items


def cursor_items_from_db(cursor):

    columns = [col[0] for col in cursor.description]
    items = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    return items


def dates_to_str(items, date_column_names):

    for column in date_column_names:
        for i in range(len(items)):
            items[i][column] = str(items[i][column])

    return items


def printv(name, variable):
    print(name, type(variable), variable)


def generate_query(bool_search_string, bool_search_number, order_by, order_type, bool_registration_date_gte, bool_registration_date_lte):

    start = """SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section,
                br_insertion, text, street, postal_code, city
            FROM ov.or_podanie_issues
            """

    where = """WHERE """
    if bool_search_string and bool_search_number:
        where += """(corporate_body_name ILIKE %(search)s OR city ILIKE %(search)s OR cin = %(search_int)s)
                """
    elif bool_search_string:
        where += """(corporate_body_name ILIKE %(search)s OR city ILIKE %(search)s)
                """
    else:
        where = """"""

    if bool_registration_date_gte or bool_registration_date_lte:
        if len(where) == 0:
            where = "WHERE "
        else:
            where += " AND "

        if bool_registration_date_gte and bool_registration_date_lte:
            where += "registration_date >= %(reg_gte)s AND registration_date <= %(reg_lte)s" + "\n"
        elif bool_registration_date_gte:
            where += "registration_date >= %(reg_gte)s" + "\n"
        else:
            where += "registration_date <= %(reg_lte)s" + "\n"

    order = "ORDER BY " + order_by + " " + order_type + "\n"

    end = """LIMIT %(limit)s
            OFFSET %(offset)s; 
        """

    query = start + where + order + end

    return query


def generate_variables(limit, offset, bool_search_string, search, bool_search_number, search_int,
                       bool_registration_date_gte, reg_gte, bool_registration_date_lte, reg_lte):

    variables = {"limit": limit, "offset": offset}

    if bool_search_string:
        variables["search"] = search

    if bool_search_number:
        variables["search_int"] = search_int

    if bool_registration_date_gte:
        variables["reg_gte"] = reg_gte

    if bool_registration_date_lte:
        variables["reg_lte"] = reg_lte

    return variables


def generate_metadata(page, per_page, pages, total):

    return {"page": page, "per_page": per_page, "pages": pages, "total": total}


def first5(request):

    query = """ 
                SELECT id, br_court_name, kind_name, cin, 
                registration_date, corporate_body_name, br_section, 
                br_insertion, text, street, postal_code, city 
                FROM ov.or_podanie_issues ORDER BY id ASC LIMIT 5;
            """

    items = OLD_cursor_items_from_db(query)

    items = dates_to_str(items, ["registration_date"])

    metadata = generate_metadata(0, 0, 0, 0)

    result = {"items": items, "metadata": metadata}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response


def get_print_pages(request):

    allParameters = request.GET
    print(allParameters)

    # page = request.GET.get('page', '1')
    # per_page = request.GET.get('per_page', '10')
    # query = request.GET.get('query', '%')
    # printv('query', query)

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
    bool_search_number = True

    search_int = 0
    try:
        search_int = int(search)
    except:
        bool_search_number = False

    if search is not None:
        bool_search_string = True
        search = "%" + search + "%"

    registration_date_gte = allParameters.get("registration_date_gte")
    bool_registration_date_gte = registration_date_gte is not None
    print(bool_registration_date_gte)
    printv("registration_date_gte", registration_date_gte)

    registration_date_lte = allParameters.get("registration_date_lte")
    bool_registration_date_lte = registration_date_lte is not None
    print(bool_registration_date_lte)
    printv("registration_date_lte", registration_date_lte)

    collumn_names = ["id", "br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name", "br_section",
                "br_insertion", "text", "street", "postal_code", "city"]
    possible_order_types = ["asc", "desc"]

    order_by = allParameters.get("order_by", "id")
    order_by = order_by.lower()
    if order_by not in collumn_names:
        order_by = "id"
    printv("order_by", order_by)

    default_order_type = "asc"
    order_type = allParameters.get("order_type", default_order_type)
    order_type = order_type.lower()
    if order_type not in possible_order_types:
        order_type = default_order_type
    printv("order_type", order_type)


    page_offset = (page_int - 1) * per_page_int

    query = generate_query(bool_search_string, bool_search_number, order_by, order_type, bool_registration_date_gte, bool_registration_date_lte)
    print(query)

    # variables = {
    #             "limit": per_page_int,
    #             "offset": page_offset,
    #             "search": search,
    #             "search_int": search_int,
    #         }
    # print(variables)

    variables = generate_variables(per_page_int, page_offset, bool_search_string, search, bool_search_number, search_int,
                                   bool_registration_date_gte, registration_date_gte, bool_registration_date_lte, registration_date_lte)
    print(variables)

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        items = cursor_items_from_db(cursor)

    items = dates_to_str(items, ["registration_date"])

    len_items = len(items)
    total = len_items
    pages = math.ceil(len_items / per_page_int)

    metadata = generate_metadata(page_int, per_page_int, pages, total)

    result = {"items": items, "metadata": metadata}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response


def post_add_row(request):
    print("post")

    print(request.POST)
    print(request.GET)
    print(request.body)


    return JsonResponse({"method": "POST"})


def delete_row(request):
    print("delete")

    return JsonResponse({"method": "DELETE"})


def debug(request):
    num1, num2 = 10, 0

    # query = """
    #             SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section,
    #                     br_insertion, text, street, postal_code, city
    #             FROM ov.or_podanie_issues
    #             ORDER BY id ASC
    #             LIMIT %(limit)s
    #             OFFSET %(offset)s;
    #         """ % {"limit": num1, "offset": num2}
    #
    # print(query)

    with connection.cursor() as cursor:

        # cursor.execute(
        #     """
        #     SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section,
        #         br_insertion, text, street, postal_code, city
        #     FROM ov.or_podanie_issues
        #     ORDER BY id ASC
        #     LIMIT %(limit)s
        #     OFFSET %(offset)s;
        #     """, {
        #     "limit": num1,
        #     "offset": num2,
        #     })

        # index = "'; select true; --"
        index = "Advertising Services s. r. o."

        cursor.execute(
            """ 
            SELECT id, corporate_body_name
            FROM ov.or_podanie_issues 
            
            WHERE corporate_body_name = %(index)s 

            """, {
            "index": index,
            })


        items = cursor.fetchone()
        print(items)

        response = True
        if items is None:
            # User does not exist
            response = False

    return JsonResponse({"debug": response})

# SELECT id, br_court_name, kind_name, cin,
# registration_date, corporate_body_name, br_section,
# br_insertion, text, street, postal_code, city
# FROM ov.or_podanie_issues
# --WHERE corporate_body_name LIKE 'Orange Slovensko'
# ORDER BY id ASC
# LIMIT 10
# OFFSET 1;
#
# --CREATE INDEX ON ov.or_podanie_issues(corporate_body_name);
#
# SELECT *
# FROM ov.or_podanie_issues
# WHERE corporate_body_name ILIKE '%orange Slovensko%';
#
# SELECT corporate_body_name, registration_date
# FROM ov.or_podanie_issues
# WHERE corporate_body_name ~*  'orange Slovensko';



