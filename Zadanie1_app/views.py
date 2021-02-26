import psycopg2
from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection

import datetime
import os

# Create your views here.


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def health(request):

    with connection.cursor() as cursor:
        cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
        row = cursor.fetchone()

    db_time = "%s" % row
    db_time = db_time.replace(',', '')
    
    # response = JsonResponse({ "pgsql": { "uptime": "%s" %row } })
    response = JsonResponse({ "pgsql": { "uptime": db_time } })

    return response


def welcome(request):

    response = JsonResponse({ "Hello": { "World": "!!!" } })

    return response


def error(request):

    print("Toto zamerne vyhodi chybu")
