FROM node:lts-alphine
WORKDIR /app
COPY . .
RUN yarn install --production
EXPOSE 7000
CMD['node','app.js']
