FROM python:3.11.6-alpine3.18
LABEL maintrainer="vidernykov.a.e@gmail.com"

ENV PYTHOUNNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user && \
    chmod +x /entrypoint.sh && \
    chown -R my_user:my_user /app

USER my_user
ENTRYPOINT ["/entrypoint.sh"]

