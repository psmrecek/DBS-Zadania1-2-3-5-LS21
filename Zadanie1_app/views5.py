import json
import math
from datetime import datetime

from django.http import JsonResponse
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q, F, Count
from django.utils.timezone import now as django_now
from .views2 import number_validator, string_validator, generate_error_response_post
from django.forms.models import model_to_dict
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

    if search_filter is None and date_filter is None:
        return ~Q(pk=None)

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

    # if order_type == 'desc':
    #     order_by = '-' + order_by

    page_offset = (page_int - 1) * per_page_int

    custom_filter = _submissions_get_generate_filter(search_string_bool, search_string, search_number_bool, search_number,
                                                     reg_date_gte_bool, reg_date_gte_convert, reg_date_lte_bool, reg_date_lte_convert)
    # print(custom_filter)

    if order_type == 'desc':
        items = models.OrPodanieIssues.objects.filter(custom_filter).order_by(F(order_by).desc(nulls_last=True)).values(
            "id", "br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name", "br_section",
            "br_insertion", "text", "street", "postal_code", "city"
        )[page_offset:(page_offset + per_page_int)]
    else:
        items = models.OrPodanieIssues.objects.filter(custom_filter).order_by(F(order_by).asc(nulls_last=True)).values(
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


def submissions_get_one(request, table_id=-1):
    print("teraz")
    podanie = None
    try:
        podanie = models.OrPodanieIssues.objects.get(id=table_id)
    except:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404,
                            json_dumps_params={'ensure_ascii': False})

    full_model_dict = _submissions_remove_from_dict(podanie)

    result = {"response": full_model_dict}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response


def _submissions_post_record_date_validator(body_json, key):
    value = ""

    try:
        value = body_json[key]
    except KeyError:
        return 0

    date_bool = True
    date = None
    try:
        date = parse_datetime(value)
    except:
        date_bool = False
    print(date)
    print(parse_datetime(value), type(value))
    if date_bool and (date is not None) and (datetime.now().year == date.year):
        return 1

    return -1


def _submissions_post_record_podanie(body_json, bulletin_id, raw_id):

    br_court_name = body_json["br_court_name"]
    kind_name = body_json["kind_name"]
    cin = body_json["cin"]
    registration_date = parse_datetime(body_json["registration_date"])
    corporate_body_name = body_json["corporate_body_name"]
    br_section = body_json["br_section"]
    br_insertion = body_json["br_insertion"]
    text = body_json["text"]
    street = body_json["street"]
    postal_code = body_json["postal_code"]
    city = body_json["city"]
    address_line = street + ", " + postal_code + " " + city

    podanie = models.OrPodanieIssues(bulletin_issue_id=bulletin_id, raw_issue_id=raw_id, br_mark="-", br_court_code="-",
                                       br_court_name=br_court_name, kind_code="-", kind_name=kind_name, cin=cin,
                                       registration_date=registration_date, corporate_body_name=corporate_body_name,
                                       br_section=br_section, br_insertion=br_insertion, text=text, address_line=address_line,
                                       street=street, postal_code=postal_code, city=city, created_at=django_now(),
                                       updated_at=django_now())
    return podanie


def _submissions_remove_from_dict(podanie):
    full_model_dict = model_to_dict(podanie)
    full_model_dict.pop("bulletin_issue", None)
    full_model_dict.pop("raw_issue", None)
    full_model_dict.pop("br_mark", None)
    full_model_dict.pop("br_court_code", None)
    full_model_dict.pop("kind_code", None)
    # full_model_dict.pop("br_insertion", None)
    full_model_dict.pop("created_at", None)
    full_model_dict.pop("updated_at", None)
    full_model_dict.pop("address_line", None)
    full_model_dict.pop("company", None)

    return full_model_dict


def submissions_post_record(request):
    request_body = request.body

    body_json = json.loads(request_body)

    # 1 = OK, 0 = missing, -1 = error
    bool_br_court_name = string_validator(body_json, "br_court_name")
    bool_kind_name = string_validator(body_json, "kind_name")
    bool_cin = number_validator(body_json, "cin")
    bool_registration_date = _submissions_post_record_date_validator(body_json, "registration_date")
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

    current_year = datetime.now().year
    last_bulletin = models.BulletinIssues.objects.order_by('-id')[0]
    insert_year = current_year
    insert_number = last_bulletin.number + 1
    if last_bulletin.year != current_year:
        insert_number = 1

    now = django_now()

    bulletin = models.BulletinIssues(year=insert_year, number=insert_number, published_at=now, created_at=now, updated_at=now)
    bulletin.save()
    bulletin_id = bulletin.pk

    raw = models.RawIssues(bulletin_issue_id=bulletin_id, file_name="-", content="-", created_at=now, updated_at=now)
    raw.save()
    raw_id = raw.pk

    podanie = _submissions_post_record_podanie(body_json, bulletin_id, raw_id)
    podanie.save()

    full_model_dict = _submissions_remove_from_dict(podanie)

    result = {"response": full_model_dict}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False}, status=201)

    return response


def _submissions_put_record_error_response(list_bools, list_names):
    text = []

    for i in range(len(list_bools)):
        if list_bools[i] == -1:
            if list_names[i] == "registration_date":
                error = {"field": list_names[i], "reasons": ["invalid_range"]}
                text.append(error)
                continue

            if list_names[i] == "cin":
                error = {"field": list_names[i], "reasons": ["not_number"]}
                text.append(error)
                continue

            error = {"field": list_names[i], "reasons": ["not_string"]}
            text.append(error)

    response = JsonResponse({"errors": text}, status=422, safe=False)
    return response


def _submissions_put_record_string_validator(body_json, key):

    try:
        value = body_json[key]
    except KeyError:
        return 0

    if not isinstance(value, str):
        return -1

    try:
        if len(value) == 0:
            return 0
    except:
        return 0

    return 1


def submissions_put_record(request, table_id=-1):
    podanie = None
    try:
        podanie = models.OrPodanieIssues.objects.get(id=table_id)
    except:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404,
                            json_dumps_params={'ensure_ascii': False})

    request_body = request.body

    body_json = json.loads(request_body)

    # 1 = OK, 0 = missing, -1 = error
    bool_br_court_name = _submissions_put_record_string_validator(body_json, "br_court_name")
    bool_kind_name = _submissions_put_record_string_validator(body_json, "kind_name")
    bool_cin = number_validator(body_json, "cin")
    bool_registration_date = _submissions_post_record_date_validator(body_json, "registration_date")
    bool_corporate_body_name = _submissions_put_record_string_validator(body_json, "corporate_body_name")
    bool_br_section = _submissions_put_record_string_validator(body_json, "br_section")
    bool_br_insertion = _submissions_put_record_string_validator(body_json, "br_insertion")
    bool_text = _submissions_put_record_string_validator(body_json, "text")
    bool_street = _submissions_put_record_string_validator(body_json, "street")
    bool_postal_code = _submissions_put_record_string_validator(body_json, "postal_code")
    bool_city = _submissions_put_record_string_validator(body_json, "city")

    list_bools = [bool_br_court_name, bool_kind_name, bool_cin, bool_registration_date, bool_corporate_body_name,
                  bool_br_section, bool_br_insertion, bool_text, bool_street, bool_postal_code, bool_city]
    list_names = ['br_court_name', 'kind_name', 'cin', 'registration_date', 'corporate_body_name', 'br_section',
                  'br_insertion', 'text', 'street', 'postal_code', 'city']

    bool_post_ok = True

    for item in list_bools:
        if item == -1:
            bool_post_ok = False

    if not bool_post_ok:
        response = _submissions_put_record_error_response(list_bools, list_names)
        return response

    for i in range(len(list_bools)):
        if list_bools[i]:
            podanie.__dict__[list_names[i]] = body_json[list_names[i]]
    podanie.updated_at = django_now()
    podanie.save()

    full_model_dict = _submissions_remove_from_dict(podanie)

    result = {"response": full_model_dict}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False}, status=201)

    return response


def submissions_delete_record(request, table_id=-1):
    podanie = None
    try:
        podanie = models.OrPodanieIssues.objects.get(id=table_id)
    except:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404,
                            json_dumps_params={'ensure_ascii': False})

    bulletin_id = podanie.bulletin_issue.pk
    raw_id = podanie.raw_issue.pk

    podanie.delete()
    raw = models.RawIssues.objects.get(id=raw_id)
    raw.delete()
    bulletin = models.BulletinIssues.objects.get(id=bulletin_id)
    bulletin.delete()


    return HttpResponse(status=204)


def submissions_url_dispatcher(request, table_id=None):

    method = request.method

    response = HttpResponse("")

    if method == 'GET':
        if table_id is None:
            response = submissions_get_pages(request)
        else:
            response = submissions_get_one(request, table_id)
    elif method == 'POST':
        response = submissions_post_record(request)
    elif method == 'PUT':
        response = submissions_put_record(request, table_id)
    elif method == 'DELETE':
        response = submissions_delete_record(request, table_id)

    return response


def _companies_get_generate_filter(search_string_bool, search_string, reg_date_gte_bool, reg_date_gte_convert,
                                   reg_date_lte_bool, reg_date_lte_convert):

    search_filter = None
    date_filter = None

    if search_string_bool:
        search_filter = (Q(name__icontains=search_string) | Q(address_line__icontains=search_string))

    if reg_date_gte_bool and reg_date_lte_bool:
        date_filter = (Q(registration_date__gte=reg_date_gte_convert) & Q(registration_date__lte=reg_date_lte_convert))
    elif reg_date_gte_bool:
        date_filter = (Q(registration_date__gte=reg_date_gte_convert))
    elif reg_date_lte_bool:
        date_filter = (Q(registration_date__lte=reg_date_lte_convert))

    if search_filter is None and date_filter is None:
        return ~Q(pk=None)

    if search_filter is None:
        return date_filter

    if date_filter is None:
        return search_filter

    custom_filter = search_filter & date_filter
    return custom_filter


def companies_get_pages(request):
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

    custom_filter = _companies_get_generate_filter(search_string_bool, search_string,
                                                     reg_date_gte_bool, reg_date_gte_convert, reg_date_lte_bool,
                                                     reg_date_lte_convert)
    # print(custom_filter)

    if order_type == 'desc':
        items = models.Companies.objects.filter(custom_filter).order_by(F(order_by).desc(nulls_last=True)).values(
            "cin", "name", "br_section", "address_line", "last_update"
        )[page_offset:(page_offset + per_page_int)]
    else:
        items = models.Companies.objects.filter(custom_filter).order_by(F(order_by).asc(nulls_last=True)).values(
            "cin", "name", "br_section", "address_line", "last_update"
        )[page_offset:(page_offset + per_page_int)]

    # items = models.Companies.objects.annotate(or_podanie_issues_count=Count('cin'))
    # print(items)
    # for i in range(10):
    #     print(items[i].cin)

    all_items = models.Companies.objects.filter(custom_filter).count()
    pages = math.ceil(all_items / per_page_int)
    metadata = {"page": page_int, "per_page": per_page_int, "pages": pages, "total": all_items}
    result = {"items": list(items), "metadata": metadata}
    result = {"items": list(items)}

    response = JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})

    return response