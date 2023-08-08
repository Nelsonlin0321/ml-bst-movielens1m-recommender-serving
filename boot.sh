#!/bin/bash
gunicorn --workers=${WORKERS:-1} --threads ${THREADS:-1} --timeout 60 --bind :${PORT:-5500} --worker-class uvicorn.workers.UvicornWorker server:app