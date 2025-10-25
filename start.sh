#!/bin/bash
# تشغيل Flask مع Gunicorn ودعم 200 نافذة متوازية
exec gunicorn app:app --workers 4 --threads 50 --bind 0.0.0.0:$PORT
