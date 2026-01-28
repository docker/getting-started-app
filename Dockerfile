FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN apk add --no-cache python3 g++ make
RUN yarn install --production
COPY . . 
CMD ["node", "src/index.js"]
EXPOSE 3000