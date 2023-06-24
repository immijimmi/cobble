:: Runs the application in the development venv, with no command line arguments and leaving the terminal visible even in the event of a crash
:: Automatically ensures any dependencies are installed before running
:: Requires a venv with compatible dependencies for the project to be installed under \venv

cd ..
venv\Scripts\python -m pip install -r requirements.txt

venv\Scripts\python -m cobble
pause
