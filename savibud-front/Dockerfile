### Stage 1: build the app
FROM node:22-alpine AS builder
WORKDIR /app

# Copy only package files first so the install layer is cached if lockfile didn't change
COPY savibud-front/package*.json ./
COPY savibud-front/.npmrc ./
RUN npm i --omit=dev

COPY savibud-front/ ./
RUN npm run build

### Stage 2: serve with nginx
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY savibud-front/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
