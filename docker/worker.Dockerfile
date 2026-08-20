FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY apps ./apps
COPY core ./core
COPY integrations ./integrations
COPY database ./database

CMD ["celery", "-A", "apps.worker.celery_app.celery_app", "worker", "--loglevel=INFO"]
