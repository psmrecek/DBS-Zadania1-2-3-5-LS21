# Generated by Django 3.1.7 on 2021-03-28 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("""
            CREATE TABLE ov.companies (
            cin BIGINT PRIMARY KEY,
            name VARCHAR,
            br_section VARCHAR,
            address_line VARCHAR,
            last_update TIMESTAMP,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT sub.cin, sub.name, sub.br_section, sub.address_line, sub.updated_at, NOW(), NOW()
        FROM (
            SELECT cin, corporate_body_name as name, br_section, address_line, created_at, updated_at, row_number() over(PARTITION by cin order by updated_at desc) rn
            FROM ov.or_podanie_issues
            WHERE cin IS NOT NULL
        ) as sub where rn = 1
        ON CONFLICT DO NOTHING;
        
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT sub.cin, sub.name, sub.br_section, sub.address_line, sub.updated_at, NOW(), NOW()
        FROM (
            SELECT cin, corporate_body_name as name, br_section, coalesce(street, ', ') || coalesce(postal_code, ' ') || coalesce(city, '') as address_line, created_at, updated_at, row_number() over(PARTITION by cin order by updated_at desc) rn
            FROM ov.likvidator_issues
            WHERE cin IS NOT NULL
        ) as sub where rn = 1
        ON CONFLICT DO NOTHING;
        
        INSERT INTO ov.companies(cin, name, address_line, last_update, created_at, updated_at)
        SELECT sub.cin, sub.name, sub.address_line, sub.updated_at, NOW(), NOW()
        FROM (
            SELECT cin, corporate_body_name as name, coalesce(street, ', ') || coalesce(postal_code, ' ') || coalesce(city, '') as address_line, created_at, updated_at, row_number() over(PARTITION by cin order by updated_at desc) rn
            FROM ov.konkurz_vyrovnanie_issues
            WHERE cin IS NOT NULL
        ) as sub where rn = 1
        ON CONFLICT DO NOTHING;
        
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT sub.cin, sub.name, sub.br_section, sub.address_line, sub.updated_at, NOW(), NOW()
        FROM (
            SELECT cin, corporate_body_name as name, br_section, coalesce(street, ', ') || coalesce(postal_code, ' ') || coalesce(city, '') as address_line, created_at, updated_at, row_number() over(PARTITION by cin order by updated_at desc) rn
            FROM ov.znizenie_imania_issues
            WHERE cin IS NOT NULL
        ) as sub where rn = 1
        ON CONFLICT DO NOTHING;
        
        INSERT INTO ov.companies(cin, name, address_line, last_update, created_at, updated_at)
        SELECT sub.cin, sub.name, sub.address_line, sub.updated_at, NOW(), NOW()
        FROM (
            SELECT cin, corporate_body_name as name, coalesce(street, ', ') || coalesce(postal_code, ' ') || coalesce(city, '') as address_line, created_at, updated_at, row_number() over(PARTITION by cin order by updated_at desc) rn
            FROM ov.konkurz_restrukturalizacia_actors
            WHERE cin IS NOT NULL
        ) as sub where rn = 1
        ON CONFLICT DO NOTHING;
        
        
        ALTER TABLE ov.or_podanie_issues
            ADD COLUMN company_id bigint,
            add constraint fk_companies 
            foreign key (company_id) 
            REFERENCES ov.companies (cin);
            
        UPDATE ov.or_podanie_issues
        SET company_id = cin;
        
        ALTER TABLE ov.likvidator_issues
            ADD COLUMN company_id bigint,
            add constraint fk_companies 
            foreign key (company_id) 
            REFERENCES ov.companies (cin);
            
        UPDATE ov.likvidator_issues
        SET company_id = cin;
        
        ALTER TABLE ov.konkurz_vyrovnanie_issues
            ADD COLUMN company_id bigint,
            add constraint fk_companies 
            foreign key (company_id) 
            REFERENCES ov.companies (cin);
            
        UPDATE ov.konkurz_vyrovnanie_issues
        SET company_id = cin;
        
        ALTER TABLE ov.znizenie_imania_issues
            ADD COLUMN company_id bigint,
            add constraint fk_companies 
            foreign key (company_id) 
            REFERENCES ov.companies (cin);
            
        UPDATE ov.znizenie_imania_issues
        SET company_id = cin;
        
        ALTER TABLE ov.konkurz_restrukturalizacia_actors
            ADD COLUMN company_id bigint,
            add constraint fk_companies 
            foreign key (company_id) 
            REFERENCES ov.companies (cin);
            
        UPDATE ov.konkurz_restrukturalizacia_actors
        SET company_id = cin;

        """)
    ]