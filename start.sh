#!/bin/bash
# تشغيل Flask مع Gunicorn ودعم 50 نافذة متوازية
exec gunicorn app:app --workers 1 --threads 50 --bind 0.0.0.0:$PORT
