#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# NUEVO: Crear el usuario administrador de forma automática
python create_admin.py