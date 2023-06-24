:: Runs the application in a development venv, with no command line arguments
:: The terminal is left visible even in the event of a crash for debugging purposes
:: Installs a venv a the \venv subfolder if none exists at this location already
:: Automatically ensures any dependencies are installed before running

cd ..

python -m venv ./venv
venv\Scripts\python -m pip install -r requirements.txt

venv\Scripts\python -m cobble
pause
