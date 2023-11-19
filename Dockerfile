FROM python

COPY requirements.txt .
COPY app ./app/

RUN [ "pip", "install", "-r", "requirements.txt"]
RUN [ "python", "app/backend/setup_db.py"]

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]