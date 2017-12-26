FROM python:3.6.4-alpine3.7

RUN apk add --no-cache git

WORKDIR /opt

RUN git clone https://github.com/appi147/thepiratebay.git

WORKDIR /opt/thepiratebay

RUN apk add --no-cache libxml2-dev
RUN apk add --no-cache libxml2
RUN apk add --update --no-cache g++ gcc libxslt-dev
RUN pip3 install -r ./requirements.txt

EXPOSE 5000

RUN sed -i 's/    APP.run()/    APP.run(host="0.0.0.0")/g' app.py

RUN cat app.py

CMD python3 app.py
