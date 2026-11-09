FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# API relativa al mismo origen; no activa simulaciones.
ENV VITE_API_URL="" VITE_USE_MOCKS=false VITE_USE_MOCKS_CLIENTE=false
RUN npm test && npm run build

FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
