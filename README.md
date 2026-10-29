# Sigma Phi Delta Mizzou New Website
## Setup Instructions
For security purposes, the website keeps the database, secret key, development environment, and the path to the admin panel *outside the git repo*, in the folder that contains it:

```
SPDWebsite/              <- put .env and db.sqlite3 here
├── .env
├── db.sqlite3
├── .venv/
└── SPDWEBSITE/          <- this git repo
    └── django/          <- manage.py
```

In that folder, you need two things:

1. The `db.sqlite3` file (which will be automatically generated unless you have a previous database you want to use)
2. A file called `.env`

Create the `.env` file to match this template
```ini
SECRET_KEY='paste here'
ADMIN_URL='admin'
ENVIRONMENT='local'
ALLOWED_HOSTS='localhost,127.0.0.1,spdmizzou.com,www.spdmizzou.com,spdmizzou.org,www.spdmizzou.org'
STORAGE_DIR='BASE_DIR.parent.parent'
```
Then paste the output of this command into the file as the `SECRET_KEY`
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Keep the single quotes around each value, since secret keys often contain characters like `$` and `#` that would otherwise be misread.

You may change the admin path to whatever you wish. The environment should be set to `'local'` on your own computer and `'production'` only on the live server, since `'production'` turns off debug mode and forces HTTPS.

`ALLOWED_HOSTS` is a comma-separated list of the domains the site answers to. Use `'localhost,127.0.0.1'` on your own computer; the live server lists the real domains.

Never commit the `.env` file. It is already listed in `.gitignore`.

## Running the Website
From the `django/` folder, with the virtual environment activated:
```bash
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

To run the tests:
```bash
python manage.py test
```
