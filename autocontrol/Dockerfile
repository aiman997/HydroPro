from python:slim
RUN mkdir -p /home/flask/app/autocontrol
WORKDIR /home/flask/app/autocontrol
COPY requirements.txt /home/flask/app/autocontrol
RUN apt update && apt upgrade -y
RUN apt install gcc -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "/home/flask/app/autocontrol/auto.py"]
