FROM node:lts

ENV CI=true
ENV PORT=8001

WORKDIR /code
COPY package.json /code/package.json
COPY package-lock.json /code/package-lock.json
# RUN npm install -g npm@5
#update npm
RUN npm install -g npm 
RUN npm ci --omit=optional --legacy-peer-deps
COPY . /code

CMD [ "npm", "start" ]