#!/bin/sh
echo "Running Server"
if [ "$DJANGO_SETTINGS_MODULE" = "Klerly.settings.local" ]; then
    python3 manage.py migrate
fi 

python3 manage.py runserver 0.0.0.0:$DJANGO_PORT 
