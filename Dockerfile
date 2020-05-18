FROM arm32v7/python:3.7-buster

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY app/ /app

WORKDIR /app
 
ENTRYPOINT [ "python", "./bme680_data_recorder.py" ]
