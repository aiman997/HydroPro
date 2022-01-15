from python:slim
RUN groupadd pipgroup && useradd -m -g pipgroup -s /bin/bash piper
RUN echo "flask ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /home/pipster
WORKDIR /home/pipster
COPY requirements.txt /home/pipster/
RUN pip install --no-cache-dir -r requirements.txt
RUN chown -R piper:pipgroup /home/pipster
USER piper
CMD [ "python3", "/opt/apps/flaskapi/app.py" ]
