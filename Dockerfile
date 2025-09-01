FROM ubuntu:24.04

ENV POSTGRES_VERSION=17


RUN apt update

###############postgres
RUN apt-get -y  install gnupg postgresql-common apt-transport-https lsb-release
RUN echo y | ./usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
RUN apt-get -y install postgresql-server-dev-$POSTGRES_VERSION

RUN apt-get -y install postgresql-$POSTGRES_VERSION
RUN sed -i 's/peer/trust/' /etc/postgresql/$POSTGRES_VERSION/main/pg_hba.conf
RUN echo "host    all    all    0.0.0.0/0     md5" >> /etc/postgresql/$POSTGRES_VERSION/main/pg_hba.conf
RUN sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/$POSTGRES_VERSION/main/postgresql.conf

###############python
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt -y install python3-pip
RUN python -m pip install --break-system-packages uv


# COPY uv.lock /uv.lock
COPY pyproject.toml /pyproject.toml
COPY start.sh /start.sh
COPY server.py /server.py
COPY create.sql /create.sql

RUN uv sync

RUN mkdir /src


EXPOSE 5432
EXPOSE 8223

ENTRYPOINT sh start.sh && /bin/bash
