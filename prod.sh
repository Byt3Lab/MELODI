#!/bin/bash
echo "Déploiement de l'application ERP..."
gunicorn -w 4 -b 127.0.0.1:8080 main:app
# hypercorn main:app --bind 127.0.0.1:8080 --workers 4
# uvicorn main:app --host 127.0.0.1 --port 8080 --workers 4
