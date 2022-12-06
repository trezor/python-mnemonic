#!/bin/bash
# Execute this file with the following command:
# ./venv_setup.sh

################ IMPORTANT!! ################
# python3 must be your default Python version!  
# Recomended version is python 3.9.7.

# Note: Please select the python iterpreter inside environment to development, also in IDE's (VSCode, PyCharm, Spyder, etc). 
# Interpreter path: /envformosa/bin/python3
##

# Update pip
python3 -m pip install --user --upgrade pip

# Install venv
python3 -m pip install --user virtualenv

# Create formosa virtual environment
python3 -m virtualenv envformosa

# Activate environment
source envformosa/bin/activate

# Automaticaly install dependencies
python3 -m pip install -r requirements.txt

# Deactive environment after running
deactivate
