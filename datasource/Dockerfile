from python:slim
RUN groupadd pipgroup && useradd -m -g pipgroup -s /bin/bash piper
RUN echo "piper ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /home/flask/app/datasource
WORKDIR /home/flask/app/datasource
COPY requirements.txt /home/flask/app/datasource
RUN pip install --no-cache-dir -r requirements.txt
RUN chown -R piper:pipgroup /home/flask
USER piper
CMD [ "python", "/home/flask/app/datasource/ds.py" ]
