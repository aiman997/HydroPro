from python:slim
RUN mkdir -p /home/flask/app/subscriber
WORKDIR /home/flask/app/subscriber
COPY requirements.txt /home/flask/app/subscriber
RUN apt update && apt upgrade -y
RUN apt install gcc -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "/home/flask/app/subscriber/sub.py" ]
