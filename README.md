# <package name>

###### <package description>

## Quickstart

- Find and replace any text surrounded with angle brackets (`<` and `>`) with the expected value as indicated inside the brackets
- Double-check any lines commented with exactly five hash symbols (`#####`) have the correct values
- Find and replace any file and folder names entirely contained inside parentheses (`(` and `)`) with the expected value as indicated inside the parentheses
- Untrack to-do.txt
- Remove any files that are not necessary for your project. File usages are as follows:
  - Core files:
    - `\(packagename)\__init__.py`
    - `\tools\testcoverage.bat`
    - `.gitignore`
    - `README.md`
    - `to-do.txt`
  - Files which facilitate running your project as an application:
    - `\(packagename)\__main__.py`
    - `\tools\start-venv.bat`
    - `requirements.txt`
    - `start.bat`
  - Files which facilitate publishing your project as a package:
    - `\tools\setup.bat`
    - `LICENSE.txt`
    - `MANIFEST.in`
    - `setup.py`
- Remove this bullet list from the readme file once complete
