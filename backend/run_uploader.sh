#!/bin/bash
if [ "$FLASK_DEBUG" == "true" ]; then
    flask run
else
    gunicorn -w 4 -b "$FLASK_RUN_HOST:$FLASK_RUN_PORT" --timeout 600 "$FLASK_APP"
fi