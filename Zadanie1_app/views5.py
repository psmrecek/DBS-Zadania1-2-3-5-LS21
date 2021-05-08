import math

from django.http import JsonResponse
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from .views2 import cursor_items_from_db, dates_to_str, date_validator
from . import models


def test(request):

    try:
        podanie = models.OrPodanieIssues.objects.get(id=1)
        print(podanie.text)
    except:
        print("-")

    try:
        comp1 = models.Companies.objects.get(cin=11111)
        print(comp1.name)
    except:
        print("-")


    response = JsonResponse({"Hello": {"World": "!!!"}})
    return response


def _submissions_get_generate_filter(search_string_bool, search_string, search_number_bool, search_number,
                                    reg_date_gte_bool, reg_date_gte_convert, reg_date_lte_bool, reg_date_lte_convert):

    search_filter = None
    date_filter = None

    if search_string_bool and search_number_bool:
        search_filter = (Q(corporate_body_name__icontains=search_string) | Q(city__icontains=search_string) | Q(cin=search_number))
    elif search_string_bool:
        search_filter = (Q(corporate_body_name__icontains=search_string) | Q(city__icontains=search_string))

    if reg_date_gte_bool and reg_date_lte_bool:
        date_filter = (Q(registration_date__gte=reg_date_gte_convert) & Q(registration_date__lte=reg_date_lte_convert))
    elif reg_date_gte_bool:
        date_filter = (Q(registration_date__gte=reg_date_gte_convert))
    elif reg_date_lte_bool:
        date_filter = (Q(registration_date__lte=reg_date_lte_convert))

    if search_filter is None:
        return date_filter

    if date_filter is None:
        return search_filter

    custom_filter = search_filter & date_filter
    return custom_filter


def submissions_get_pages(request):
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

    search_string = allParameters.get('query')
    search_string_bool = False
    search_number_bool = True

    search_number = 0
    try:
        search_number = int(search_string)
    except:
        search_number_bool = False

    if search_string is not None:
        search_string_bool = True

    registration_date_gte = allParameters.get("registration_date_gte")
    reg_date_gte_bool = True
    reg_date_gte_convert = None
    try:
        reg_date_gte_convert = parse_datetime(registration_date_gte)
    except:
        reg_date_gte_bool = False

    registration_date_lte = allParameters.get("registration_date_lte")
    reg_date_lte_bool = True
    reg_date_lte_convert = None
    try:
        reg_date_lte_convert = parse_datetime(registration_date_lte)
    except:
        reg_date_lte_bool = False

    collumn_names = ["id", "br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name",
                     "br_section",
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

    if order_type == 'desc':
        order_by = '-' + order_by

    page_offset = (page_int - 1) * per_page_int

    custom_filter = _submissions_get_generate_filter(search_string_bool, search_string, search_number_bool, search_number,
                                                     reg_date_gte_bool, reg_date_gte_convert, reg_date_lte_bool, reg_date_lte_convert)
    # print(custom_filter)

    items = models.OrPodanieIssues.objects.filter(custom_filter).order_by(order_by).values(
        "id", "br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name", "br_section",
        "br_insertion", "text", "street", "postal_code", "city"
    )[page_offset:(page_offset + per_page_int)]

    all_items = models.OrPodanieIssues.objects.filter(custom_filter).count()
    pages = math.ceil(all_items / per_page_int)
    metadata = {"page": page_int, "per_page": per_page_int, "pages": pages, "total": all_items}
    result = {"items": list(items), "metadata": metadata}
    # result = {"items": list(items)}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response


def submissions_post_record(request):
    pass


def submissions_put_record(request):
    pass


def submissions_delete_record(request):
    pass


def submissions_url_dispatcher(request):

    method = request.method

    response = HttpResponse("")

    if method == 'GET':
        response = submissions_get_pages(request)
    elif method == 'POST':
        response = submissions_post_record(request)
    elif method == 'PUT':
        response = submissions_put_record(request)
    elif method == 'DELETE':
        response = submissions_delete_record(request)

    return response