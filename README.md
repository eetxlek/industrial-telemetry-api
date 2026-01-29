# 🚀 Telemetry API - Arquitectura Hexagonal

API REST para gestión de telemetría industrial con arquitectura hexagonal, sistema de integridad blockchain-like y seguridad JWT.

## 📋 Características

### ✅ Arquitectura Hexagonal
- **Dominio puro**: Sin dependencias de frameworks o bases de datos
- **Puertos**: Interfaces abstractas (`TelemetryRepository`, `TelemetryEventPublisher`)
- **Adaptadores**: Implementaciones concretas (PostgreSQL, REST, Logging)

### ✅ Modelo de Dominio
- **Planta**: Representa una instalación industrial
- **Sensor**: Dispositivos de medición en plantas
- **Telemetría**: Registros de datos con integridad de hash
- **Métrica**: Agregaciones de datos (promedio, min, max)

### ✅ Sistema de Integridad
Sistema blockchain-like con hashes encadenados:
```
payload_hash = SHA256(sensor_id + valor + timestamp + previous_hash)
```

Cada registro se vincula al anterior, garantizando:
- Inmutabilidad de datos históricos
- Detección de manipulación
- Auditoría completa

### ✅ Seguridad
- **JWT**: Autenticación basada en tokens
- **Roles**: Control de acceso (productor, consumidor, admin)
- **Rate Limiting**: Protección contra abuso (100 req/min)

### ✅ Endpoints

| Endpoint | Método | Rol | Descripción |
|----------|--------|-----|-------------|
| `/auth/token` | POST | - | Obtener token JWT |
| `/telemetry` | POST | productor | Registrar telemetría |
| `/metrics` | GET | consumidor | Obtener métricas |
| `/health` | GET | - | Health check |

## 🏗️ Estructura del Proyecto

```
telemetry-api/  
├── src/  
│   ├── domain/                    # Dominio puro (sin dependencias)  
│   │   ├── entities/  
│   │   │   ├── planta.py  
│   │   │   ├── sensor.py  
│   │   │   └── telemetria.py     # Con lógica de hashing  
│   │   └── value_objects/  
│   │       └── metrica.py  
│   │  
│   ├── application/               # Lógica de aplicación  
│   │   ├── ports/                 # Interfaces (puertos)  
│   │   │   ├── telemetry_repository.py  
│   │   │   └── telemetry_event_publisher.py  
│   │   └── use_cases/             # Casos de uso  
│   │       ├── registrar_telemetria.py  
│   │       └── obtener_metricas.py  
│   │  
│   └── infrastructure/            # Adaptadores  
│       ├── adapters/  
│       │   ├── rest/              # Adaptador REST  
│       │   │   ├── endpoints.py  
│       │   │   ├── schemas.py  
│       │   │   └── dependencies.py  
│       │   └── persistence/       # Adaptador PostgreSQL  
│       │       ├── models.py  
│       │       ├── postgresql_repository.py  
│       │       └── logging_event_publisher.py  
│       ├── config/  
│       │   ├── database.py  
│       │   └── security.py  
│       └── main.py                # Punto de entrada  
│  
├── requirements.txt  
├── docker-compose.yml  
├── Dockerfile  
├── init_db.sql  
└── README.md  
```

## 🚀 Inicio Rápido

### Opción 1: Con Docker (Recomendado)

```bash
# Clonar repositorio
cd telemetry-api

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

La API estará disponible en: http://localhost:8000

### Opción 2: Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar PostgreSQL (manual o Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=telemetry_db \
  -p 5432:5432 \
  postgres:15-alpine

# Ejecutar la aplicación
cd src/infrastructure
python main.py
```

## 📚 Uso de la API

### 1. Autenticación

Primero obtén un token JWT:

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "productor",
    "password": "productor123"
  }'
```

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Usuarios de Prueba

| Usuario    | Contraseña    | Roles                        |
|------------|---------------|------------------------------|
| productor  | productor123  | productor                    |
| consumidor | consumidor123 | consumidor                   |
| admin      | admin123      | productor, consumidor, admin |

### 2. Registrar Telemetría (Rol: productor)

```bash
curl -X POST http://localhost:8000/telemetry \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "223e4567-e89b-12d3-a456-426614174001",
    "valor": 25.5,
    "timestamp": "2024-01-15T10:30:00"
  }'
```

Respuesta:
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174001",
  "sensor_id": "223e4567-e89b-12d3-a456-426614174001",
  "valor": 25.5,
  "timestamp": "2024-01-15T10:30:00",
  "payload_hash": "a1b2c3d4e5f6...",
  "previous_hash": "0"
}
```

### 3. Obtener Métricas (Rol: consumidor)

```bash
# Métricas de todos los sensores
curl -X GET http://localhost:8000/metrics \
  -H "Authorization: Bearer <tu_token>"

# Filtrar por sensor
curl -X GET "http://localhost:8000/metrics?sensor_id=223e4567-e89b-12d3-a456-426614174001" \
  -H "Authorization: Bearer <tu_token>"

# Filtrar por rango de fechas
curl -X GET "http://localhost:8000/metrics?fecha_inicio=2024-01-01T00:00:00&fecha_fin=2024-01-31T23:59:59" \
  -H "Authorization: Bearer <tu_token>"
```

Respuesta:
```json
[
  {
    "sensor_id": "223e4567-e89b-12d3-a456-426614174001",
    "sensor_nombre": "Sensor Temperatura Panel 1",
    "valor_promedio": 24.8,
    "valor_minimo": 20.0,
    "valor_maximo": 30.0,
    "total_registros": 150,
    "unidad": "°C"
  }
]
```

## 🔐 Seguridad

### JWT (JSON Web Tokens)
- Tokens con expiración (30 minutos por defecto)
- Firma HMAC-SHA256
- Incluye roles del usuario

### Control de Acceso Basado en Roles (RBAC)
- **productor**: Puede registrar telemetría
- **consumidor**: Puede consultar métricas
- **admin**: Acceso completo

### Rate Limiting
- Límite global: 100 requests/minuto por IP
- Protección contra ataques DDoS
- Headers de rate limit en respuestas

### Integridad de Datos
Sistema de hashes encadenados:
1. Cada registro tiene un `payload_hash`
2. Incluye referencia al `previous_hash`
3. Cualquier modificación rompe la cadena
4. Verificación de integridad disponible

## 🗄️ Base de Datos

### Esquema PostgreSQL

```sql
-- Tabla plantas
CREATE TABLE plantas (
    id UUID PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    activa BOOLEAN DEFAULT true
);

-- Tabla sensores
CREATE TABLE sensores (
    id UUID PRIMARY KEY,
    planta_id UUID REFERENCES plantas(id),
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    activo BOOLEAN DEFAULT true
);

-- Tabla telemetría (con integridad blockchain-like)
CREATE TABLE telemetria (
    id UUID PRIMARY KEY,
    sensor_id UUID REFERENCES sensores(id),
    valor FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64) NOT NULL DEFAULT '0'
);
```

### Inicializar datos de prueba

```bash
# Conectar a PostgreSQL
docker exec -it telemetry_postgres psql -U postgres -d telemetry_db

# Ejecutar script
\i /docker-entrypoint-initdb.d/init_db.sql
```

## 📖 Documentación Interactiva

Una vez iniciada la API, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Prueba completa del flujo

```bash
# 1. Obtener token como productor
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"productor","password":"productor123"}' \
  | jq -r '.access_token')

# 2. Registrar telemetría
curl -X POST http://localhost:8000/telemetry \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "223e4567-e89b-12d3-a456-426614174001",
    "valor": 25.5
  }'

# 3. Obtener token como consumidor
TOKEN_CONS=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"consumidor","password":"consumidor123"}' \
  | jq -r '.access_token')

# 4. Consultar métricas
curl -X GET http://localhost:8000/metrics \
  -H "Authorization: Bearer $TOKEN_CONS"
```

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y ajusta:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/telemetry_db
SECRET_KEY=tu-clave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
RATE_LIMIT_PER_MINUTE=100
```

## 📊 Monitoreo

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
# Docker
docker-compose logs -f api

# Local
# Los logs se imprimen en consola
```

## 🎯 Principios de Arquitectura Hexagonal

### Dominio Puro
El dominio no conoce:
- Frameworks (FastAPI, SQLAlchemy)
- Bases de datos (PostgreSQL)
- Protocolos (HTTP, REST)

### Puertos (Interfaces)
Contratos que el dominio define:
- `TelemetryRepository`: Persistencia
- `TelemetryEventPublisher`: Eventos

### Adaptadores (Implementaciones)
Implementan los puertos:
- `PostgreSQLTelemetryRepository`
- `LoggingEventPublisher`
- `REST API (FastAPI)`

### Ventajas
✅ Testeable: Dominio sin dependencias  
✅ Mantenible: Cambios aislados  
✅ Flexible: Intercambio de adaptadores  
✅ Escalable: Independencia de componentes

## 🚀 Próximos Pasos

- [ ] Implementar event publisher con Kafka/RabbitMQ
- [ ] Añadir caché con Redis
- [ ] Implementar WebSocket para telemetría en tiempo real
- [ ] Añadir métricas con Grafana o Prometheus
- [ ] Implementar tests unitarios y de integración
- [ ] Añadir CI/CD con GitHub Actions


## 👨‍💻 Autor

Estibaliz Extaburu Backend Developer

Desarrollado como ejemplo de arquitectura hexagonal con FastAPI.
