FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev git curl \
        # weasyprint system dependencies
        libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
        libpangoft2-1.0-0 libgdk-pixbuf2.0-0 \
        libffi-dev shared-mime-info libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["sh", "start.sh"]
