django-mangekampen-trondheim
============================

New mangekampen applicatin written in Python/Django

## Setup for dev environment
* Install python-dev packages on your computer
* Create a virtualenv and install the requirements listed in the attached file.
    * Source and then pip install -r requirements_local.txt
* python manage.py syncdb
* python manage.py migrate
* python manage.py collectstatic
* python manage.py runserver

## Setup for prod environment
* Install python-dev packages on your computer (required for _imaging module etc)
* Install postgres-dev packages(in order to compile psycopg2)
* Install libevent-dev packages(required to compile gevent2)
* Create a virtualenv and install the requirements listed in the attached file.
    * Source and then pip install -r requirements_local.txt
* python manage.py syncdb
* python manage.py migrate
* python manage.py collectstatic
*
