## How to run this project?

1. Install python
2. Open the folder containing all files of this project using a terminal
3. create a virtual environment ```python -m venv venv```
4. activate virtual environment -> Windows: ```.\venv\Scripts\activate.bat``` or on Linux: ```source ./venv/bin/activate```
5. Install all dependencies ```pip install -r requirements.txt```
6. Run on localhost ```uvicorn main:app --reload```

Important info:
- Any time you want to stop hosting on localhost press ```ctrl + c```
- An alternative to hosting on your localhost is using the ```run_test.py``` script using ```python run_test.py``` instead of the 6th step. This should host the website on your entire home network.
- Repeated hosting after the first setting up only requires steps 4-6
