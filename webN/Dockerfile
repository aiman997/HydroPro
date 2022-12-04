#from python:slim
from python:3.9-slim
RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask
RUN echo "flask ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /home/flask/app/webN
WORKDIR /home/flask/app/webN
RUN apt update && apt upgrade -y
RUN apt install gcc -y
RUN pip install --upgrade pip
RUN apt-get -y install libpq-dev gcc 
RUN pip install psycopg2 
COPY requirements.txt /home/flask/app/webN
RUN pip install --no-cache-dir -r requirements.txt
RUN chown -R flask:flaskgroup /home/flask
USER flask
#CMD ["python3", "/home/flask/app/webN/app.py"]
#####ENTRYPOINT ["/usr/local/bin/gunicorn", "--bind", ":8006", "app:app", "--reload", "--workers", "1"]
