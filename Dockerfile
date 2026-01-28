FROM node:lts-alpine
WORKDR /app
COPY . .
RUN yarn and install --production
CMD ["node" "src/index.js"]
EXPOSE 3000
