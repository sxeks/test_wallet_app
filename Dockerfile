FROM python:3.12.0

EXPOSE 8000

WORKDIR /

COPY /apps ./apps
COPY main.py ./main.py
COPY alembic.ini ./alembic.ini
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --no-cache --upgrade -r requirements.txt