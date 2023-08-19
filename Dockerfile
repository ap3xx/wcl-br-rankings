FROM python:3.8.10-slim-buster

RUN mkdir -p /app

COPY ingestor-requirements.txt /var
RUN pip install -r /var/ingestor-requirements.txt

ADD ingestor /app
WORKDIR /app

CMD python3 main.py
