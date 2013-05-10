django-mangekampen-trondheim
============================

New mangekampen application written in Python/Django.

## Dev setup using Vagrant - RECOMMENDED
* Install Vagrant and Virtualbox. 
        
        http://virtualbox.org
        http://vagrantup.com

* Provision the Ubuntu 12.04 LTS virtual machine to run the web site using vagrant

        vagrant up

* Connect to the vagrant box. Default user pass is vagrant/vagrant
        
        vagrant ssh 

### The following steps are INSIDE the virtual machine you just SSHed to.

* Create a virtualenv and install the requirements needed to run the application.

        mkvirtualenv mk
        cd /vagrant
        pip install -r local_requirements.txt

* Create a default config file for django and run the dev server.

        cd mangekampentrondheim
        cp mangekampentrondheim/local_settings.py.template mangekampentrondheim/local_settings.py

* Syncronize core django tables to the database

        python manage.py syncdb
        # Say NO to creating a superuser at this point, as we do not have a UserProfile table yet.

* Create database schema for mangekampen application
    
        python manage.py migrate

* Now you can create a superuser to log in to the system

        python manage.py createsuperuser

* Start the web server and begin development
    
        python manage.py runserver <ip of virtual machine>:<port number>

        # NOTE: You can get the local ip from the command 'ip a' at the prompt. See the eth0 interface.


## Dev setup locally
* Install python-dev packages on your computer
* Install libevent-dev packages(required to compile gevent2)
* Create a virtualenv 
* Source the newly created virtualenv and then install requirements
    
        source path_to_virtualenv/bin/activate
        pip install -r local_requirements.txt

* Create your own local_settings.py to use local database.

        cp local_settings.py.template local_settings.py

* Syncronize core django tables to the database

        python manage.py syncdb
        # Say NO to creating a superuser at this point, as we do not have a UserProfile table yet.

* Create database schema for mangekampen application
    
        python manage.py migrate

* Now you can create a superuser to log in to the system with

        python manage.py createsuperuser

* Start the web server and begin development
    
        python manage.py runserver <ip to listen on>:<port number>


## Production setup
* Install python-dev packages on your computer (required for _imaging module etc)
* Install postgres-dev packages(in order to compile psycopg2)
* Install libevent-dev packages(required to compile gevent2)
* Create a virtualenv 
* Source and the newly created virtualenv and then install requirements

        pip install -r requirements_local.txt

* Syncronize core django tables to the database

        python manage.py syncdb
        # Say NO to creating a superuser at this point, as we do not have a UserProfile table yet.

* Create database schema for mangekampen application

        python manage.py migrate

* Now you can create a superuser to log in to the system with

        python manage.py createsuperuser

* Collect static content and move it to static hosting location

        python manage.py collectstatic

* Test your setup using a gunicorn server

        python manage.py run_gunicorn -b 0.0.0.0:<some port>

If this works you can now set up nginx, apache or similar to proxy to the
gunicorn server.  Alternatively you can use wsgi-modules for apache to proxy
through the built in modules. Also you must set up static file hosting for the
locations defined in settings.py for media and static files.

## For mangekampen trondheim server stuff.
Run the automatic deployment script in the mangekampen user home folder.

    ./deploy-mangekampen.sh

Note that this script requires sudo access to /usr/sbin/service and write access to /home/mangekampentrondheim for static files.
