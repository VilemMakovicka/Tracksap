### [Project setup]
cmd => ```python -m venv venv```<br>
pycharm terminal => ```.\venv\Scripts\activate.ps1```<br>
cmd => ```.\venv\Scripts\activate.bat```<br>
cmd => ```pip install -r requirements.txt```<br>
<br>
### [Pycharm setup]<br>
File>Settings>Interpreter>Add Interpreter>Vybrat .\venv\Scripts\python.exe<br>
<br>
### [Hosting setup]<br>
uvicorn main:app --reload