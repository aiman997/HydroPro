from python:slim
RUN mkdir -p /home/flask/app/datasource
WORKDIR /home/flask/app/datasource
COPY requirements.txt /home/flask/app/datasource
RUN apt update && apt upgrade -y
RUN apt install gcc -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "/home/flask/app/datasource/ds.py" ]
