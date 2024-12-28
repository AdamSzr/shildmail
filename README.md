# shildmail
Projekt na pracę magisterską

## steps to run locally

1. python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python3 manage.py runserver


<!--
WITH wynik AS (
    SELECT t1.*, t2.*
    FROM tabela1 t1
    JOIN tabela2 t2 ON t1.email = t2.email
)
SELECT *
FROM wynik
WHERE nazwa_kolumny = 'wartość';


INSERT INTO users (
    email, 
    password, 
    realname, 
    maildir
) VALUES (
    'simple@adamszreiber.pl', 
    '{PLAIN}simple', 
    'Simple Maker',
    'simple_maker/'
);
-->