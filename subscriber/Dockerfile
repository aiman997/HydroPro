FROM python:slim

RUN mkdir -p /app/subscriber

WORKDIR /app/subscriber

COPY requirements.txt /app/subscriber

RUN apt update && apt upgrade -y

RUN apt install gcc -y

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/app/subscriber/sub.py" ]
