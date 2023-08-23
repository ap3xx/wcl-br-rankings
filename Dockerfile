FROM python:3.8.10-slim-buster

RUN mkdir -p /app

COPY ingest-requirements.txt /var
RUN pip install -r /var/ingest-requirements.txt

ADD ingest /app
WORKDIR /app

CMD python3 app.py
