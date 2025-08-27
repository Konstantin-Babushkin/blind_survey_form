#!/bin/bash

# Деплой скрипт для blind survey приложения

set -e

echo "🚀 Начинаем деплой blind survey приложения..."

# Проверяем, что мы на сервере с Traefik
if ! docker network ls | grep -q traefik; then
    echo "❌ Traefik сеть не найдена. Убедитесь, что Traefik запущен."
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Останавливаем старый контейнер если есть
echo "🛑 Останавливаем старые контейнеры..."
docker-compose -f docker-compose.prod.yml down || true

# Собираем новый образ
echo "🔨 Собираем Docker образ..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Запускаем новый контейнер
echo "🚀 Запускаем новый контейнер..."
docker-compose -f docker-compose.prod.yml up -d

# Проверяем статус
echo "✅ Проверяем статус контейнера..."
docker-compose -f docker-compose.prod.yml ps

# Показываем логи
echo "📋 Последние логи:"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo "🎉 Деплой завершен! Приложение доступно по адресу: https://survey.timofeev41.com"
