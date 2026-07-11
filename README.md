![logo](/static/images/headerlogo.png)
**Tracksap** is music streaming website. The project was originaly my university project and currently serves as a way to show my technical skills.


![screenshot](/readme_resources/screenshot_1.png)

## How to self host this project yourself?

1. Install **python**
2. In a terminal, open the folder on your device that contains the contents of this repository
3. Create a virtual environment ```python -m venv venv```
4. Activate virtual environment: 
    - Windows: ```.\venv\Scripts\activate.bat``` 
    - Linux: ```source ./venv/bin/activate```
5. Install all dependencies ```pip install -r requirements.txt```
6. Host on your device ```uvicorn main:app --reload```

Important info:
- Any time you want to stop hosting on localhost press ```ctrl + c```
- An alternative to hosting on your localhost is using the ```run_test.py``` script using ```python run_test.py``` instead of the 6th step. This should host the website on your entire home network.
- Repeated hosting after the first setting up only requires steps 4-6
