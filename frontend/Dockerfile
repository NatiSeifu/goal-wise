# syntax=docker/dockerfile:1

FROM node:22-alpine AS build

ARG VITE_API_BASE_URL

ENV NPM_CONFIG_FUND=false \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    VITE_API_BASE_URL=${VITE_API_BASE_URL}

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . ./
RUN npm run build

FROM caddy:2-alpine AS production

WORKDIR /app

COPY Caddyfile ./
RUN caddy fmt Caddyfile --overwrite

COPY --from=build /app/dist ./dist

EXPOSE 3000

CMD ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]
