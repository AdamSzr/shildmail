# shildmail
Projekt na pracę magisterską

## steps to run locally

1. python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python3 manage.py runserver



## PostgreSQL

``` bash
psql -U mailreader -d mail -h localhost -p 5432
password: mailreader
```
---
`sudo -u postgres psql`

---

### Tworzenie tabeli użytkownika

``` sql
CREATE TABLE users (
  email VARCHAR NOT NULL,
  password VARCHAR NOT NULL,
  realname VARCHAR NOT NULL,
  maildir INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT now(),
  last_login TIMESTAMP NULL
);
```
``` sql
mail=# \d users
                           Table "public.users"
   Column   |            Type             | Collation | Nullable | Default 
------------+-----------------------------+-----------+----------+---------
 email      | text                        |           | not null | 
 password   | text                        |           | not null | 
 realname   | text                        |           | not null | 
 maildir    | text                        |           | not null | 
 created    | timestamp with time zone    |           | not null | now()
 last_login | timestamp without time zone |           |          | 
Indexes:
    "users_pkey" PRIMARY KEY, btree (email)
Referenced by:
    TABLE "passkeys" CONSTRAINT "fk_username" FOREIGN KEY (username) REFERENCES users(email) ON DELETE CASCADE
```
### Tworzenie tabeli sessji django
``` sql
CREATE TABLE django_session (
    session_key VARCHAR NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);
```

### Tworzenie tabeli passkeys
``` sql
CREATE TABLE passkeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) NOT NULL,
    credential_id BYTEA NOT NULL,
    credential_public_key BYTEA NOT NULL,
    credential_type VARCHAR(255) NOT NULL,
    aaguid VARCHAR(255) NOT NULL,
    transports TEXT[] DEFAULT '{}',
    is_discoverable BOOLEAN DEFAULT FALSE,
    sign_count INTEGER NOT NULL,
    registration_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    authenticator_attachment VARCHAR(255),
    public_key_algorithm INTEGER NOT null,
    CONSTRAINT fk_username FOREIGN KEY (username) REFERENCES users (email) ON DELETE CASCADE
);
```
### Dodanie użytkownika w SQL
```sql
INSERT INTO users (email, password, realname, maildir) VALUES ('secure@adamszreiber.pl', '{SHA512}ZqLXiozTDwDQ+OQ0NHMc48k1HOnH9mvBzS4QXtyZS+CpEGyFu37tCaQh3jb0rw3C8kvcZPhkXOfv0/2Qm5N4Xg==', 'Secure User', 'secure_user/');
```

### Zmiana hasła użytkownika w SQL
```sql
UPDATE users
SET password = '{SHA512}YEx+jYQ9s94cstHkkm4St3zD8fwQxE/8w0gbOI53u1ySLNFMqHPskMBv5CLqEjgbkGnpoqHC1xm+FRrJOVgh7w=='
WHERE email = 'sigma@adamszreiber.pl';
```

