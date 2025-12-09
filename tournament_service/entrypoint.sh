#!/bin/sh
set -e

# Apply database migrations
python manage.py migrate --noinput

# Run tests
pytest

# If tests pass, start the dev server
python manage.py runserver 0.0.0.0:8000