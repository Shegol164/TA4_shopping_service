FROM postgres:15-alpine

# Установка необходимых утилит
RUN apk add --no-cache postgresql-client

# Установка переменных окружения
ENV POSTGRES_DB=${POSTGRES_DB:-TA4_shopping_service_db}
ENV POSTGRES_USER=${POSTGRES_USER:-user}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-2543474Pasha}

EXPOSE 5432