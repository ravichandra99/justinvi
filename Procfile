web: gunicorn core.wsgi --log-file -

release: python manage.py migrate inventory && python manage.py migrate transactions && python manage.py migrate
