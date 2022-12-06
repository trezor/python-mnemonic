@echo off
REM Double click in this file to execute.

@echo off
REM Update pip
py -m pip install --upgrade pip

@echo off
REM Install venv
py -m pip install --user virtualenv

@echo off
REM Create formosa virtual environment
py -m venv envformosa

@echo off
REM Activate environment and automaticaly install dependencies
.\envformosa\Scripts\activate && py -m pip install --upgrade pip && py -m pip install -r requirements.txt




