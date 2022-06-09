FROM python:latest

COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /app

ADD chat ./chat
COPY manage.py db.sqlite3 ./

COPY entrypoint.sh .
ENTRYPOINT ["sh", "entrypoint.sh"]




