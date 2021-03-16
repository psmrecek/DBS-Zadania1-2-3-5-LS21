# project-str12-lancaric-psmrecek
project-str12-lancaric-psmrecek created by GitHub Classroom

Riešenie zadania č. 2

Vytvorenie aplikačného serveru s API (End-point) s pripojením na databázu

Projekt bol vypracovaný v programovacom jazyku Python s pomocou Django frameworku.

Adresa servera: https://fiit-dbs-xsmrecek-app.azurewebsites.net

Adresa riešenia zadania 1: https://fiit-dbs-xsmrecek-app.azurewebsites.net/v1/health

Vzorové vstupy pre zadanie 2:

GET: 
https://fiit-dbs-xsmrecek-app.azurewebsites.net/v1/ov/submissions?page=1&per_page=10&order_by=br_court_name&order_type=asc&registration_date_lte=2020-11-06%2015%3A14%3A32&registration_date_gte=2019-04-01%2013%3A11%3A06&query=Tren%C4%8D%C3%ADn

POST: 
https://fiit-dbs-xsmrecek-app.azurewebsites.net/v1/ov/submissions

Vzorové RAW BODY pre POST:
`{
    "br_court_name": "Trenčín",
    "kind_name": "Neviem",
    "cin": 424242,
    "registration_date": "2021-03-13",
    "corporate_body_name": "Breakdown",
    "br_section": "sro",
    "br_insertion": "123",
    "text": "Toto zadanie trvalo dlhšie, než som čakal",
    "street": "Kazimírova 6",
    "postal_code": "91101",
    "city": "Trenčín"
}`

DELETE: https://fiit-dbs-xsmrecek-app.azurewebsites.net/v1/ov/submissions/42