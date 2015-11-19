#!/bin/sh
python3 manage.py makemigrations
python3 manage.py syncdb
python3 manage.py collectstatic --noinput
