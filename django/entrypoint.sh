#!/bin/bash
# entrypoint.sh

# データベースマイグレーション
python manage.py migrate

# Djangoサーバーを実行
python manage.py runserver 0.0.0.0:8000
