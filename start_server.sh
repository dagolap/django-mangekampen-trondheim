#! /bin/sh
python mangekampentrondheim/manage.py collectstatic --noinput
python mangekampentrondheim/manage.py run_gunicorn -b 0.0.0.0:$PORT -w 3 -k gevent --preload 
