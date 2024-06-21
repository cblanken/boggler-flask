#!/bin/sh
if [ "$INIT_DB" ]; then
    rm -f .db_no_init
fi
poetry run flask --app main --debug run --no-reload 
