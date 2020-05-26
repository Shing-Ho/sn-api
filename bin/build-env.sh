#!/usr/bin/env bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."
VENV_DIR="$BASE_DIR/.venv"

path_to_python3=$(which python3.7)
if [[ ! -x $path_to_python3 ]]; then
  echo "Error: Please install Python 3.7, pyenv preferred."
  echo "Example: brew install pyenv"
  echo "         pyenv install 3.7.3"
  exit 1
fi

python3.7 -mvenv $VENV_DIR
source $VENV_DIR/bin/activate

python $BASE_DIR/setup.py develop