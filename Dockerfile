FROM python:3.6-slim

COPY ./requirements.txt /app/requirements.txt

COPY ./email_list /app/email_list

COPY ./last_processed_datetime /app/last_processed_datetime

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ./message-alert.py /app/message-alert.py

CMD python message-alert.py
