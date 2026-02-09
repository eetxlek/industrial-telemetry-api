#!/bin/sh
set -e

echo "⏳ Esperando a la base de datos..."
sleep 5

echo "📦 Ejecutando migraciones Alembic..."
alembic upgrade head

echo "🚀 Arrancando API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000