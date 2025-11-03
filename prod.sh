#!/bin/bash
echo "Déploiement de l'application ERP..."
# gunicorn -w 4 -b 127.0.0.1:8080 main:app
hypercorn main:app --bind 0.0.0.0:5000 --workers 4