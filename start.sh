#!/bin/sh

service postgresql start
psql -U postgres -d postgres -c "create user root with password 'root';"
psql -U postgres -d postgres -c "create database test_db owner root;"

psql -U root -d test_db -c "create schema test_schema;"

psql -U root -d test_db -a -f create.sql

#uvicorn main:app --reload

uv run server.py
