FROM python:3.11-slim

WORKDIR /app

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/ apps/api/
COPY packages/  packages/
COPY data/processed/ data/processed/

ENV PYTHONPATH=/app
ENV DATA_DIR=data/processed

EXPOSE 8000
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
