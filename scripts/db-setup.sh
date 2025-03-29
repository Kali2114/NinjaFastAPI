#!/bin/sh

export PGUSER="kamileg"

psql -d postgres -c "CREATE DATABASE ninjadb;"

psql -d ninjadb -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"