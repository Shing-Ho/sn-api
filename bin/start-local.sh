#!/usr/bin/env bash
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."
SRC_DIR="$BASE_DIR/src"
APP_DIR="$SRC_DIR/api"

export PYTHON_PATH="$APP_DIR"
python $APP_DIR/manage.py runserver