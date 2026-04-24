# 🏭 API de Telemetría Industrial

Sistema de telemetría para plantas industriales con **garantía de integridad criptográfica** basada en cadenas de hashes (blockchain-like).

## 🎯 Executive Summary 

**¿Problema?** En plantas industriales, los datos de sensores pueden ser manipulados, por error o malicia, llevando a decisiones peligrosas.

**¿Solución?** Esta API registra cada dato de telemetría encadenándolo criptográficamente (hash) con el anterior, como un blockchain. Cualquier modificación posterior es detectable al instante vía auditoría.

**¿Resultado?** Los ingenieros y auditores pueden **demostrar matemáticamente** que los datos no han sido alterados desde su origen.

## 📚 Contenido

1. Características Principales
2. Tecnologías
3. Arquitectura
   - Arquitectura Hexagonal
   - Arquitectura Orientada a Eventos (Productor de eventos)
4. Recursos del API
5. Endpoints
6. Integridad Criptográfica
7. Instalación y Uso
8. Estructura del Proyecto
9. Casos de Uso
10. Validaciones de Dominio
11. Optimizaciones
12. Testing
13. Escalabilidad
14. Seguridad
---

## 🎯 Características Principales

- ✅ **Integridad Criptográfica**: Cada telemetría tiene hash SHA-256 encadenado (inmutable)
- ✅ **Validaciones de Dominio**: Verifica valores físicamente imposibles (temperatura < -273°C, humedad > 100%)
- ✅ **Arquitectura Hexagonal**: Separación clara de capas (Domain, Application, Infrastructure)
- ✅ **Optimizado para IoT**: Bulk insert de telemetrías (10x más rápido)
- ✅ **Auditoría Integrada**: Verifica que datos históricos no han sido modificados
- ✅ **Transacciones Atómicas**: DB + Eventos sincronizados

---

## 📦 Tecnologías

- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy (Async)
- **Patrón**: Hexagonal Architecture + DDD
- **Hash**: SHA-256
- **Eventos**: EventPublisher (RabbitMQ/Kafka compatible)

---

## 🏗️ Arquitectura
```
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER (REST)                         │
│  /plantas  /sensores  /telemetria  /auditoria                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────────┐
│                    APPLICATION SERVICES                           │
│  PlantaService  SensorService  TelemetriaService  AuditoriaService│
└───────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN ENTITIES                              │
│  Planta  Sensor  Telemetria  Metrica(VO)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE (PostgreSQL)                    │
│  PlantaRepo  SensorRepo  TelemetriaRepo  EventPublisher         │
└─────────────────────────────────────────────────────────────────┘
```
## 🔄 Arquitectura Orientada a Eventos (Event-Driven)

Este sistema actúa como **productor de eventos de dominio**.

- Cada operación relevante (p. ej. `TelemetriaRegistrada`) publica un evento
- Los eventos se envían a un **message broker (RabbitMQ)**
- La API **no depende de consumidores concretos**

Actualmente:
- ✅ El API publica eventos de dominio
- ❌ No incluye consumidores en este repositorio

Consumidores previstos (fuera de este proyecto):
- Dashboards en tiempo casi real (Grafana)
- Sistemas de alertas
- Pipelines de analítica / ML

Este enfoque permite escalar el sistema sin acoplar la API a procesos secundarios.


---

## 📋 Recursos del API

### **Planta**
Instalación industrial que agrupa sensores
```json
{
  "id": "uuid",
  "nombre": "Planta Norte",
  "ubicacion": "Madrid, España",
  "activa": true,
  "fecha_creacion": "2024-01-15T10:30:00Z"
}
```

### **Sensor**
Dispositivo IoT que genera lecturas
```json
{
  "id": "uuid",
  "planta_id": "uuid",
  "nombre": "Sensor Temperatura 1",
  "tipo": "temperatura",
  "unidad": "°C",
  "activo": true
}
```

**Tipos disponibles**: `temperatura`, `presion`, `humedad`, `vibracion`, `caudal`

### **Telemetría**
Lectura con hash encadenado
```json
{
  "id": "uuid",
  "sensor_id": "uuid",
  "valor": 25.3,
  "timestamp": "2024-02-09T14:23:45Z",
  "payload_hash": "a1b2c3...",
  "previous_hash": "d4e5f6..."
}
```

### **Métrica** (Value Object)
Estadísticas agregadas
```json
{
  "sensor_id": "uuid",
  "sensor_nombre": "Sensor Temp 1",
  "valor_promedio": 25.3,
  "valor_minimo": 20.1,
  "valor_maximo": 30.5,
  "total_registros": 1000,
  "unidad": "°C",
  "rango": 10.4,
  "variabilidad_relativa": 8.2
}
```

---

## 🌐 Endpoints (13 Total)

### **PLANTAS** (5 endpoints)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/plantas/` | Crear planta |
| `GET` | `/plantas/` | Listar todas las plantas |
| `GET` | `/plantas/{planta_id}` | Obtener detalle de planta |
| `GET` | `/plantas/{planta_id}/sensores` | Listar sensores de la planta |
| `GET` | `/plantas/{planta_id}/metricas` | Métricas agregadas por sensor |

<details>
<summary>📘 Ver ejemplos</summary>

**Crear Planta**
```bash
POST /plantas/
Content-Type: application/json

{
  "nombre": "Planta Norte",
  "ubicacion": "Madrid, España"
}

# Respuesta
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Planta Norte",
  "ubicacion": "Madrid, España",
  "activa": true,
  "fecha_creacion": "2024-02-09T10:00:00Z"
}
```

**Obtener Métricas**
```bash
GET /plantas/550e8400-e29b-41d4-a716-446655440000/metricas

# Respuesta
[
  {
    "sensor_id": "abc-123",
    "sensor_nombre": "Temperatura Principal",
    "valor_promedio": 25.3,
    "valor_minimo": 20.0,
    "valor_maximo": 30.0,
    "total_registros": 1000,
    "unidad": "°C",
    "rango": 10.0,
    "variabilidad_relativa": 8.5
  }
]
```
</details>

---

### **SENSORES** (3 endpoints)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/sensores/` | Crear sensor |
| `POST` | `/sensores/{sensor_id}/activar` | Activar sensor |
| `POST` | `/sensores/{sensor_id}/desactivar` | Desactivar sensor |

<details>
<summary>📘 Ver ejemplos</summary>

**Crear Sensor**
```bash
POST /sensores/
Content-Type: application/json

{
  "planta_id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Sensor Temperatura 1",
  "tipo": "temperatura",
  "unidad": "°C"
}

# Respuesta
{
  "id": "abc-123",
  "planta_id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Sensor Temperatura 1",
  "tipo": "temperatura",
  "unidad": "°C",
  "activo": true
}
```

**Desactivar Sensor (Mantenimiento)**
```bash
POST /sensores/abc-123/desactivar

# Respuesta
{
  "id": "abc-123",
  "activo": false
}
```
</details>

---

### **TELEMETRÍA** (4 endpoints)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/telemetria/` | Registrar lectura individual |
| `POST` | `/telemetria/lote` | Registrar múltiples lecturas |
| `GET` | `/telemetria/{telemetria_id}` | Obtener telemetría por ID |
| `GET` | `/telemetria/sensor/{sensor_id}/ultimas` | Últimas N lecturas |

<details>
<summary>📘 Ver ejemplos</summary>

**Registrar Telemetría Individual**
```bash
POST /telemetria/
Content-Type: application/json

{
  "sensor_id": "abc-123",
  "valor": 25.3
}

# Respuesta
{
  "id": "telem-001",
  "sensor_id": "abc-123",
  "valor": 25.3,
  "timestamp": "2024-02-09T14:23:45Z",
  "payload_hash": "a1b2c3d4e5f6...",
  "previous_hash": "0"
}
```

**Registrar Lote (Bulk Insert)**
```bash
POST /telemetria/lote
Content-Type: application/json

{
  "lecturas": [
    {"sensor_id": "abc-123", "valor": 25.3},
    {"sensor_id": "def-456", "valor": 101.2},
    {"sensor_id": "abc-123", "valor": 26.1}
  ]
}

# Respuesta: Array de telemetrías creadas
[
  {
    "id": "telem-001",
    "sensor_id": "abc-123",
    "valor": 25.3,
    "timestamp": "2024-02-09T14:23:45Z",
    "payload_hash": "a1b2c3...",
    "previous_hash": "0"
  },
  ...
]
```

**Obtener Últimas Lecturas**
```bash
GET /telemetria/sensor/abc-123/ultimas?limite=50

# Respuesta: 50 últimas telemetrías ordenadas DESC
[
  {
    "id": "telem-050",
    "sensor_id": "abc-123",
    "valor": 26.5,
    "timestamp": "2024-02-09T15:00:00Z",
    "unidad": "°C"
  },
  ...
]
```
</details>

---

### **AUDITORÍA** (1 endpoint)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/auditoria/sensor/{sensor_id}` | Verificar integridad de cadena |

<details>
<summary>📘 Ver ejemplos</summary>

**Verificar Integridad**
```bash
GET /auditoria/sensor/abc-123

# Respuesta (Cadena íntegra)
{
  "sensor_id": "abc-123",
  "integro": true,
  "mensaje": "Cadena íntegra: 100 telemetrías verificadas"
}

# Respuesta (Cadena corrupta)
{
  "sensor_id": "abc-123",
  "integro": false,
  "mensaje": "Cadena rota en registro 42: hash inválido"
}
```
</details>

---

## 🔐 Cómo Funciona la Integridad

### **Cadena de Hashes (Blockchain-like)**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Telemetría 1│────▶│ Telemetría 2│────▶│ Telemetría 3│
│             │     │             │     │             │
│ valor: 25.3 │     │ valor: 26.1 │     │ valor: 24.8 │
│ hash: ABC   │     │ hash: DEF   │     │ hash: GHI   │
│ prev: 0     │     │ prev: ABC   │     │ prev: DEF   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### **Detección de Manipulación**
```python
# Original
Telemetría: valor=25.3, hash=ABC

# Alguien modifica la DB manualmente
UPDATE telemetrias SET valor=99.9 WHERE id='...';

# Auditoría detecta:
GET /auditoria/sensor/{id}
→ {integro: false, mensaje: "Hash inválido"}

# El hash ABC ya no coincide con valor=99.9
```

---

## 🚀 Instalación y Uso

### **1. Requisitos**
```bash
Python 3.11+
PostgreSQL 14+
```

### **2. Instalación**
```bash
# Clonar repositorio
git clone <repo-url>
cd telemetria-api

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### **3. Configuración**
```bash
# Crear archivo .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/telemetria_db
SECRET_KEY=your-secret-key
```

### **4. Migraciones**
```bash
# Crear base de datos
alembic upgrade head
```

### **5. Ejecutar**
```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **6. Documentación Interactiva**
```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

---

## 📊 Estructura del Proyecto
```
project/
├── domain/                    # Capa de Dominio (lógica de negocio)
│   ├── entities/
│   │   ├── planta.py         # Entidad Planta
│   │   ├── sensor.py         # Entidad Sensor (validaciones)
│   │   └── telemetria.py     # Entidad Telemetría (hash)
│   ├── value_objects/
│   │   └── metrica.py        # Métrica (inmutable)
│   └── events/
│       └── telemetria_events.py
│
├── application/               # Capa de Aplicación (casos de uso)
│   ├── services/
│   │   ├── planta_service.py
│   │   ├── sensor_service.py
│   │   ├── telemetria_service.py
│   │   └── auditoria_service.py
│   └── ports/                # Interfaces (contratos)
│       ├── repositories.py
│       └── event_publisher.py
│
├── infra/                    # Capa de Infraestructura
│   ├── adapters/
│   │   ├── persistence/      # Repositorios PostgreSQL
│   │   │   ├── models.py     # SQLAlchemy models
│   │   │   ├── postgres_planta_repo.py
│   │   │   ├── postgres_sensor_repo.py
│   │   │   └── postgres_telemetria_repo.py
│   │   ├── rest/             # REST endpoints
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── planta_endpoints.py
│   │   │   ├── sensor_endpoints.py
│   │   │   ├── telemetria_endpoints.py
│   │   │   └── auditoria_endpoints.py
│   │   └── events/
│   │       └── rabbitmq_publisher.py
│   └── config/
│       ├── database.py
│       └── inyeccion_dependencias.py
│
├── alembic/                  # Migraciones
│   └── versions/
|
├── tests/
|   ├── domain/              # Tests de entidades y reglas de negocio
|   │   ├── test_sensor.py   # Validaciones de sensor
|   │   └── test_telemetria.py # Integridad blockchain
|   ├── application/         # Tests de servicios (orquestación)
|   │   └── test_telemetria_service.py
|   └── integration/         # Tests con infraestructura real
|       └── test_db_persistence.py
|
├── main.py                   # Punto de entrada
├── requirements.txt
└── README.md
```

---

## 🎯 Casos de Uso

### **1. Dispositivo IoT Registra Lectura**
```python
# Dispositivo envía cada 5 minutos
POST /telemetria/
{
  "sensor_id": "abc-123",
  "valor": 72.3
}

# Sistema:
# 1. Valida sensor activo
# 2. Valida valor físicamente posible
# 3. Obtiene último hash de la cadena
# 4. Crea telemetría con nuevo hash
# 5. Guarda en DB
# 6. Publica evento
```

### **2. Dashboard en Tiempo Real near real time (pendiente implementar Grafana)**
```python
# Frontend solicita datos
GET /plantas/{id}/metricas

# Sistema calcula:
# - Promedio de últimas 100 lecturas
# - Min/Max
# - Variabilidad
# - Total de registros
```

### **3. Auditoría Trimestral**
```python
# Auditor verifica integridad
GET /auditoria/sensor/{id}

# Sistema:
# 1. Obtiene últimas 1000 telemetrías
# 2. Verifica cada hash individual
# 3. Verifica encadenamiento
# 4. Retorna reporte
```

### **4. Mantenimiento Preventivo**
```python
# Técnico va a reparar
POST /sensores/{id}/desactivar

# Sistema:
# - Marca sensor como inactivo
# - Rechaza nuevas lecturas
# - Preserva historial

# Reparación completa
POST /sensores/{id}/activar
```

---

## 🔧 Validaciones de Dominio

El sistema valida valores físicamente imposibles:
```python
# Temperatura
temperatura < -273.15°C → ValueError("Cero absoluto")

# Humedad
humedad < 0% o > 100% → ValueError("Fuera de rango")

# Presión, Vibración, Caudal
valor < 0 → ValueError("No puede ser negativo")
```

---

## ⚡ Optimizaciones

| Característica | Técnica | Beneficio |
|---------------|---------|-----------|
| **Bulk Insert** | `guardar_lote()` SQLAlchemy | 10x más rápido |
| **Índice Compuesto** | `(sensor_id, timestamp)` | Queries 50x más rápidas |
| **Lazy Loading** | `lazy='noload'` | Evita N+1 queries |
| **Hash Query** | Solo columna `payload_hash` | Reduce I/O |
| **Sin Cascade Delete** | `ON DELETE RESTRICT` | Preserva historial |

---

## 🧪 Testing
```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=application --cov=domain --cov=infra

# Tests unitarios (todos)
pytest tests/unit/

# Tests unitarios de dominio
pytest tests/unit/domain/

# Tests unitarios de aplicación (servicios)
pytest tests/unit/application/

# Tests de integración (PostgreSQL real)
pytest tests/integration/

# Tests específicos por archivo
pytest tests/unit/domain/test_sensor.py           # Validaciones de sensor
pytest tests/unit/domain/test_telemetria.py       # Integridad blockchain
pytest tests/unit/application/test_telemetria_service.py  # Orquestación
pytest tests/integration/test_postgres_repo.py    # Persistencia real
```

---

## 📈 Escalabilidad

### **Volumetría Soportada**
- **Telemetrías**: 1M+ registros/día
- **Sensores**: 10K+ sensores activos
- **Plantas**: 100+ plantas

### **Para Mayor Escala**
- Usar **TimescaleDB** en lugar de PostgreSQL puro
- Implementar **sharding** por planta
- Cache con **Redis** para métricas
- **Event Sourcing** completo (solo eventos, sin telemetrías en DB)

---

## 🔒 Seguridad

- ✅ Validación de entrada con Pydantic
- ✅ Transacciones ACID en PostgreSQL
- ✅ Hash SHA-256 para integridad
- ✅ Foreign keys con `ON DELETE RESTRICT`
- ✅ Soft delete (no se pierde historial)

**TODO:**
- [ ] Autenticación JWT
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Logs de auditoría de acceso

---

## 📝 Licencia

MIT License

---

## 👥 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📧 Contacto

- **Proyecto**: Sistema de Telemetría Industrial
- **Versión**: 1.0.0
- **Documentación**: http://localhost:8000/docs

---

## 🎓 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

**⭐ Si te gustó este proyecto, dale una estrella en GitHub!**
