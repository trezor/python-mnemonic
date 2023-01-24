# Run formosa
if [ -f "./envformosa/bin/activate" ]; then
    
    echo "The dependencies are installed, if you need update then please run './venv_setup.sh'"
    
    # Running application from env
    ./envformosa/bin/python ./src/mnemonic/GUI_qt.py
    
    # If this is an old directory and our requirements
    #       changed in the meantime you should run "./venv_setup.sh"
else
    echo "The dependencies are not Installed yet, running './venv_setup.sh' first."
    
    # Installing dependencies
    ./venv_setup.sh
     
    # Running application from env
    ./envformosa/bin/python ./src/mnemonic/GUI_qt.py
fi
