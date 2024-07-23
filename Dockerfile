FROM postgres:latest

RUN apt -y update && \
    apt -y upgrade && \
    apt -y install python3 \
                   python3-venv \
                   python3-pip

COPY . /iot
RUN chmod 777 -R /iot
WORKDIR /iot

USER postgres

RUN initdb && \
    pg_ctl start && \
    python3 -m venv .venv && \
    .venv/bin/pip install -r requirements.txt && \
    .venv/bin/python models.py all

EXPOSE 8080/tcp

CMD pg_ctl start && \
    .venv/bin/python main.py
