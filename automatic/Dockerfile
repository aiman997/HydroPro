from python:slim
RUN mkdir -p /home/flask/app/automatic
WORKDIR /home/flask/app/automatic
COPY requirements.txt /home/flask/app/automatic
RUN apt update && apt upgrade -y
RUN apt install gcc -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "/home/flask/app/automatic/automatic.py"]
