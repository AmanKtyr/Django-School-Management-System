#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python SMS/manage.py collectstatic --noinput
python SMS/manage.py migrate