FROM node:20.1.0-alpine3.17 AS build

WORKDIR /app

RUN rm -rf ./*
COPY package.json ./
COPY package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM node:20.1.0-alpine3.17

WORKDIR /app

COPY --from=build /app/build .
COPY --from=build /app/package.json .
COPY --from=build /app/node_modules ./node_modules

CMD ["node", "index.js"]