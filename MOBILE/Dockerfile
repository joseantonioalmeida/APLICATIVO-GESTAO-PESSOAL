# syntax=docker/dockerfile:1.7
# Versão web do aplicativo (Flutter) servida por nginx.
# O endereço da API é gravado na compilação (API_URL) e precisa ser acessível
# pelo NAVEGADOR de quem usa o aplicativo.

FROM debian:bookworm-slim AS build
ARG FLUTTER_VERSION=3.47.9
ARG API_URL=http://localhost:8000
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl unzip xz-utils ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch "${FLUTTER_VERSION}" https://github.com/flutter/flutter.git /opt/flutter
ENV PATH="/opt/flutter/bin:$PATH"
RUN flutter config --no-analytics --enable-web \
    && flutter precache --web
WORKDIR /app
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get
COPY . .
RUN flutter build web --release --no-wasm-dry-run --dart-define=API_URL="${API_URL}"

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build/web /usr/share/nginx/html
EXPOSE 8080
