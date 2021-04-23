# 🚀 Tradingbot (Work in Progress) 🚧

## Installation

`pip install -r requirements.txt`

## Run the program

Run the program once

`python3 -m tradingbot`

Run the program when on file changes (make sure you have installed [nodemon](https://nodemon.io/))

`nodemon --watch tradingbot --watch strategies -e py --exec python3 -m tradingbot`

Run typechecking

`mypy --namespace-packages ./tradingbot/main.py`

`nodemon --watch tradingbot --watch strategies -e py --exec mypy --namespace-packages ./tradingbot/main.py`

## Virtual Env

Create a virtual env for the project
`conda create -n tradingbot_env python=3.8.3`

List all env available
`conda env list`

Switch to the env
`conda activate tradingbot_env`

Exit the current venv
`conda deactivate`

Freeze packages
`pip freeze > requirements.txt`

## Pip

`pip install --upgrade pip`

## Install TA-Lib

On ubuntu
https://sachsenhofer.io/install-ta-lib-ubuntu-server/

## Running python on background

https://janakiev.com/blog/python-background/
