django-mangekampen-trondheim
============================

New mangekampen applicatin written in Python/Django

## Setup for dev environment
* Install python-dev packages on your computer
* Install libevent-dev packages(required to compile gevent2)
* Create a virtualenv and install the requirements listed in the attached file.
    * Source and then pip install -r requirements_local.txt
* python manage.py syncdb
    * Say NO to creating a superuser at this point, as we do not have a UserProfile table yet.
* python manage.py migrate
* python manage.py createsuperuser
    * Now we have the required tables to store all the user information
* python manage.py runserver <ip to listen on>:<port number>


## Setup for prod environment
* Install python-dev packages on your computer (required for _imaging module etc)
* Install postgres-dev packages(in order to compile psycopg2)
* Install libevent-dev packages(required to compile gevent2)
* Create a virtualenv and install the requirements listed in the attached file.
    * Source and then pip install -r requirements_local.txt
* python manage.py syncdb
    * Say NO to creating a superuser at this point, as we do not have a UserProfile table yet.
* python manage.py migrate
* python manage.py createsuperuser
    * Now we have the required tables to store all the user information
* python manage.py collectstatic
* python manage.py run_gunicorn -b 0.0.0.0:<some port>

You can now set up nginx, apache or similar to proxy to the gunicorn server.
Alternatively you can use wsgi-modules for apache to proxy through the built in
modules. Also you must set up static file hosting for the locations defined in
settings.py for media and static files.
