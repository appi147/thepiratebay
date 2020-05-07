FROM python:3.6.4-alpine3.7

RUN apk add --no-cache git

COPY requirements.txt requirements.txt

RUN apk add --no-cache libxml2-dev && \
    apk add --no-cache libxml2 && \
    apk add --update --no-cache g++ gcc libxslt-dev && \
    pip3 install -r ./requirements.txt

WORKDIR /opt

RUN mkdir -p thepiratebay
WORKDIR /opt/thepiratebay

COPY . .

RUN ["chmod", "+x", "entrypoint.sh"]

ENTRYPOINT ["./entrypoint.sh", "$API_PORT" ]