FROM python:3.6.4-alpine3.7

RUN apk add --no-cache git

ENV BASE_URL=https://thepiratebay.org/

COPY requirements.txt requirements.txt

RUN apk add --no-cache libxml2-dev && \
    apk add --no-cache libxml2 && \
    apk add --update --no-cache g++ gcc libxslt-dev && \
    pip3 install -r ./requirements.txt


WORKDIR /opt

COPY . .

WORKDIR /opt/thepiratebay

EXPOSE 5000

CMD python3 app.py
