import json
import math
from datetime import datetime

from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection


# Create your views here.


def url_dispatcher(request):

    method = request.method

    response = HttpResponse("")

    if method == 'GET':
        response = get_print_pages(request)
    elif method == 'POST':
        response = post_add_row(request)
    elif method == 'DELETE':
        response = delete_row(request)

    return response


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


def generate_query_get(bool_search_string, bool_search_number, order_by, order_type, bool_registration_date_gte, bool_registration_date_lte):

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


def generate_query_metadata(bool_search_string, bool_search_number, bool_registration_date_gte, bool_registration_date_lte):

    start = """ SELECT COUNT(id)
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

    query = start + where

    return query


def generate_variables_get(limit, offset, bool_search_string, search, bool_search_number, search_int,
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


def generate_metadata(page, per_page, variables, bool_search_string, bool_search_number, bool_registration_date_gte, bool_registration_date_lte):

    query = generate_query_metadata(bool_search_string, bool_search_number, bool_registration_date_gte, bool_registration_date_lte)

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        items = cursor.fetchall()

    try:
        all_items = items[0][0]
    except:
        all_items = 0

    pages = math.ceil(all_items / per_page)

    return {"page": page, "per_page": per_page, "pages": pages, "total": all_items}


def date_validator(date_string):

    try:
        date_string = date_string.replace("Z", "+00:00")
        date = datetime.fromisoformat(date_string)
        bool_valid = True
    except:
        bool_valid = False

    return bool_valid


def get_print_pages(request):

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
    bool_registration_date_gte = date_validator(registration_date_gte)

    registration_date_lte = allParameters.get("registration_date_lte")
    bool_registration_date_lte = date_validator(registration_date_lte)

    collumn_names = ["id", "br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name", "br_section",
                "br_insertion", "text", "street", "postal_code", "city"]
    possible_order_types = ["asc", "desc"]

    order_by = allParameters.get("order_by", "id")
    order_by = order_by.lower()
    if order_by not in collumn_names:
        order_by = "id"

    default_order_type = "desc"
    order_type = allParameters.get("order_type", default_order_type)
    order_type = order_type.lower()
    if order_type not in possible_order_types:
        order_type = default_order_type

    page_offset = (page_int - 1) * per_page_int

    query = generate_query_get(bool_search_string, bool_search_number, order_by, order_type, bool_registration_date_gte, bool_registration_date_lte)

    variables = generate_variables_get(per_page_int, page_offset, bool_search_string, search, bool_search_number, search_int,
                                       bool_registration_date_gte, registration_date_gte, bool_registration_date_lte, registration_date_lte)

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        items = cursor_items_from_db(cursor)

    items = dates_to_str(items, ["registration_date"])

    metadata = generate_metadata(page_int, per_page_int, variables, bool_search_string, bool_search_number,
                                 bool_registration_date_gte, bool_registration_date_lte)

    result = {"items": items, "metadata": metadata}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response


def string_validator(body_json, key):

    try:
        value = body_json[key]
    except KeyError:
        return 0

    try:
        if len(value) == 0:
            return 0
    except:
        return 0

    return 1


def number_validator(body_json, key):
    value = 0

    try:
        value = body_json[key]
    except KeyError:
        return 0

    if isinstance(value, int):
        return 1
    else:
        return -1


def date_validator_post(body_json, key):
    value = ""

    try:
        value = body_json[key]
    except KeyError:
        return 0

    if date_validator(value):
        now = datetime.now()
        value = value.replace("Z", "+00:00")
        date = datetime.fromisoformat(value)
        if now.year == date.year:
            return 1

    return -1


def generate_error_response_post(list_bools, list_names):
    text = []

    for i in range(len(list_bools)):
        if list_bools[i] == 0:
            error = {"field": list_names[i], "reasons": ["required"]}
            text.append(error)

        if list_bools[i] == -1 and list_names[i] == "registration_date":
            error = {"field": list_names[i], "reasons": ["invalid_range"]}
            text.append(error)

        if list_bools[i] == -1 and list_names[i] == "cin":
            error = {"field": list_names[i], "reasons": ["not_number"]}
            text.append(error)

    response = JsonResponse({"errors": text}, status=422, safe=False)
    return response


def insert_bulletin_post():
    now = datetime.now()
    current_year = now.year

    query_last_item = """
                        SELECT id, year, number, published_at
                        FROM ov.bulletin_issues
                        ORDER BY id DESC
                        LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(query_last_item)
        items = cursor.fetchall()

    insert_year = current_year
    insert_number = items[0][2] + 1
    if items[0][1] != current_year:
        insert_number = 1

    query_insert = """
                    INSERT INTO ov.bulletin_issues(year, number, published_at, created_at, updated_at)
                    VALUES (%(year)s, %(number)s, CURRENT_DATE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id;
    """

    variables = {"year": insert_year, "number": insert_number}

    with connection.cursor() as cursor:
        cursor.execute(query_insert, variables)
        return_id = cursor.fetchall()

    return return_id[0][0]


def insert_raw_post(bulletin_id_given):

    query = """
            INSERT INTO ov.raw_issues(bulletin_issue_id, file_name, content, created_at, updated_at)
            VALUES (%(bulletin_id)s, '-', '-', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
    """
    variables = {"bulletin_id": bulletin_id_given}

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        return_id = cursor.fetchall()

    return return_id[0][0]


def insert_podanie(body_json, id_bulletin, id_raw):

    query = """
            INSERT INTO ov.or_podanie_issues(bulletin_issue_id, raw_issue_id, br_mark, br_court_code, br_court_name, kind_code, kind_name,
								 cin, registration_date, corporate_body_name, 
								 br_section, br_insertion, text, address_line, street, postal_code, city, created_at, updated_at)
            VALUES (%(bid)s, %(rid)s, '-', '-', %(bcn)s, '-', %(kn)s, %(cin)s, %(rd)s, %(cbn)s, %(bs)s, 
            %(bi)s, %(text)s, %(al)s, %(street)s, %(pc)s, %(city)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, br_court_name, kind_name, cin, registration_date, corporate_body_name, 
								 br_section, br_insertion, text, street, postal_code, city;
    """

    br_court_name = body_json["br_court_name"]
    kind_name = body_json["kind_name"]
    cin = body_json["cin"]
    registration_date = body_json["registration_date"]
    corporate_body_name = body_json["corporate_body_name"]
    br_section = body_json["br_section"]
    br_insertion = body_json["br_insertion"]
    text = body_json["text"]
    street = body_json["street"]
    postal_code = body_json["postal_code"]
    city = body_json["city"]
    address_line = street + ", " + postal_code + " " + city

    variables = {"bid": id_bulletin, "rid": id_raw, "bcn": br_court_name, "kn": kind_name, "cin": cin,
                 "rd": registration_date, "cbn": corporate_body_name, "bs": br_section, "bi": br_insertion,
                 "text": text, "al": address_line, "street": street, "pc": postal_code, "city": city}

    with connection.cursor() as cursor:
        cursor.execute(query, variables)
        items = cursor_items_from_db(cursor)

    items = dates_to_str(items, ["registration_date"])

    result = {"response": items}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False}, status=201)

    return response


def post_add_row(request):

    request_body = request.body

    body_json = json.loads(request_body)

    # 1 = OK, 0 = missing, -1 = error
    bool_br_court_name = string_validator(body_json, "br_court_name")
    bool_kind_name = string_validator(body_json, "kind_name")
    bool_cin = number_validator(body_json, "cin")
    bool_registration_date = date_validator_post(body_json, "registration_date")
    bool_corporate_body_name = string_validator(body_json, "corporate_body_name")
    bool_br_section = string_validator(body_json, "br_section")
    bool_br_insertion = string_validator(body_json, "br_insertion")
    bool_text = string_validator(body_json, "text")
    bool_street = string_validator(body_json, "street")
    bool_postal_code = string_validator(body_json, "postal_code")
    bool_city = string_validator(body_json, "city")

    list_bools = [bool_br_court_name, bool_kind_name, bool_cin, bool_registration_date, bool_corporate_body_name,
                  bool_br_section, bool_br_insertion, bool_text, bool_street, bool_postal_code, bool_city]
    list_names = ['br_court_name', 'kind_name', 'cin', 'registration_date', 'corporate_body_name', 'br_section',
                  'br_insertion', 'text', 'street', 'postal_code', 'city']

    bool_post_ok = True

    for item in list_bools:
        if item != 1:
            bool_post_ok = False

    if not bool_post_ok:
        response = generate_error_response_post(list_bools, list_names)
        return response

    bulletin_id = insert_bulletin_post()
    raw_id = insert_raw_post(bulletin_id)
    response = insert_podanie(body_json, bulletin_id, raw_id)

    return response


def delete_row(request, table_id=-1):

    query_podanie = """
            DELETE FROM ov.or_podanie_issues
            WHERE id = %(id)s
            RETURNING *;
            """

    query_bulletin = """
            DELETE FROM ov.bulletin_issues
            WHERE id = %(id)s;
            """

    query_raw = """
            DELETE FROM ov.raw_issues
            WHERE id = %(id)s;
            """

    variables = {"id": table_id}

    with connection.cursor() as cursor:
        cursor.execute(query_podanie, variables)
        items = cursor.fetchall()

    if len(items) > 0:
        try:
            bulletin_id = items[0][1]
            raw_id = items[0][2]
        except:
            pass

        variables_raw = {"id": raw_id}
        with connection.cursor() as cursor:
            cursor.execute(query_raw, variables_raw)

        variables_bulletin = {"id": bulletin_id}
        with connection.cursor() as cursor:
            cursor.execute(query_bulletin, variables_bulletin)

    if len(items) == 0:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404, json_dumps_params={'ensure_ascii': False})
    else:
        return HttpResponse(status=204)
