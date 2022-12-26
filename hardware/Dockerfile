FROM python:slim

RUN mkdir -p /app/hardware

WORKDIR /app/hardware

COPY requirements.txt /app/hardware

RUN apt update && apt upgrade -y

RUN apt install gcc -y

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/app/hardware/rpi.py" ]
