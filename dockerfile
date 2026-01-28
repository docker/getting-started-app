FROM node:25-alpine3.22
WORKDIR /app
COPY . /app/

RUN apk update && apk add --no-cache python3 g++  make
#instalar as dependencias do projeto 
RUN yarn install --production
CMD ["node", "src/index.js"]

EXPOSE 80
