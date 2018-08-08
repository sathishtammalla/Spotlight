#!/bin/sh
# flask db upgrade
source venv/bin/activate
flask run --host=0.0.0.0
#exec gunicorn -b :5000 --access-logfile - --error-logfile - spotlight:app
exec gunicorn -b :5000  --access-logfile - --error-logfile - spotlight:app