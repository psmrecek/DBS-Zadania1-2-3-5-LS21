# project-str12-lancaric-psmrecek
project-str12-lancaric-psmrecek created by GitHub Classroom

Riešenie zadania č. 5

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

Vzorový vstup pre zadanie 3:

https://fiit-dbs-xsmrecek-app.azurewebsites.net/v1/companies/?page=2&per_page=13&order_by=or_podanie_issues_count&order_type=asc&last_update_lte=2020-11-21&last_update_gte=2019-11-30&query=Modrý

V AIS je okrem čísla commitu a zdrojových súborov pre Zadanie 3 aj alternatívna query pre migrácie, ktorá funguje rovnako ako tá použitá v zadaní, ale je naozaj JEDNA.

Zadanie 5:

Zadanie 5 funguje podobne ako zadanie 2 a 3.

Pridaná je metóda PUT pre úpravu jedného záznamu a metóda GET pre zobrazenie jedného záznamu.

Vzorový vstup pre PUT:

https://fiit-dbs-xsmrecek-app.azurewebsites.net/v2/ov/submissions/3519145

Vzorové RAW BODY pre PUT:
`{
    "kind_name": "zmena1",
    "cin": 111111
}`

Vzorový vstup pre GET 1:

https://fiit-dbs-xsmrecek-app.azurewebsites.net/v2/ov/submissions/2974514

