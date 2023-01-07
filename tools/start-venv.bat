:: Runs the application in the development venv, with no command line arguments and without displaying a terminal
:: Automatically ensures any dependencies are installed before running
:: Requires a venv with compatible dependencies for the project to be installed under \venv

cd ..
venv\Scripts\python -m pip install -r requirements.txt

start venv\Scripts\pythonw -m <package folder name>
