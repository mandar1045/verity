# Static UI served by nginx (the compose `web` service). Build context: repo root.
FROM node:20-alpine AS build
WORKDIR /app
ARG VITE_API_URL=http://localhost:8000
COPY contracts/types.ts contracts/types.ts
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci --no-audit --no-fund
COPY frontend frontend
RUN cd frontend && VITE_API_URL=$VITE_API_URL npx vite build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
