FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install uuid@8.3.2
COPY . .
EXPOSE 3000
CMD ["node","src/index.js"]


