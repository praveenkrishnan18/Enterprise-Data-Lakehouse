### POSTGRE SQL QUERIES TO CLEAN UP THE DATA

SELECT * FROM public.source_stream_backup
CREATE TABLE airbyte_backup AS
SELECT * FROM "__SOURCE____STREAM_".contacts;

SELECT * FROM airbyte_backup

### TO REMOVE UNNECESSARY COLUMNS

DO $$
DECLARE
    col RECORD;
BEGIN
    FOR col IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='airbyte_backup'
          AND column_name NOT IN (
            'properties_clv',
            'properties_email',
            'properties_phone',
            'properties_company',
            'properties_lastname',
            'properties_firstname',
            'properties_deal_value',
            'properties_lead_source',
            'properties_created_date',
            'properties_lifecyclestage'
          )
    LOOP
        EXECUTE format('ALTER TABLE airbyte_backup DROP COLUMN IF EXISTS %I;', col.column_name);
    END LOOP;
END $$;

### TO CHANGE COLUMN NAME

CREATE TABLE airbyte_contacts AS
SELECT
    properties_firstname   AS first_name,
    properties_lastname    AS last_name,
    properties_email       AS email,
    properties_phone       AS phone,
    properties_company     AS company,
    properties_lead_source AS lead_source,
    properties_lifecyclestage AS lifecycle_stage,
    properties_deal_value  AS deal_value,
    properties_clv         AS clv,
    properties_created_date AS created_date
FROM airbyte_backup;

### TO REMOVE NULL VALUES

DELETE FROM airbyte_contacts
WHERE phone IS NULL;

### TO FORMAT PHONE NUMBERS

UPDATE airbyte_contacts
SET phone = REGEXP_REPLACE(phone, '\D', '', 'g')
WHERE phone IS NOT NULL;

### TO ROUND OF VALUES

ALTER TABLE airbyte_contacts
    ALTER COLUMN deal_value TYPE numeric(20,2) USING ROUND(deal_value::numeric, 2),
    ALTER COLUMN clv TYPE numeric(20,2) USING ROUND(clv::numeric, 2);

### TO VIEW THE FINAL OUTPUT

SELECT * FROM airbyte_contacts;