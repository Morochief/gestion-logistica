# Sistema de Gestión Logística - Documentación de API

## Visión General

Esta API REST proporciona funcionalidades completas para la gestión de un sistema logístico de transporte, incluyendo CRTs (Cartas de Porte), MICs (Manifiestos de Carga), usuarios, transportadoras, remitentes, y más.

## Base URL
```
http://localhost:5000/api
```

## Autenticación

La API utiliza JWT (JSON Web Tokens) para autenticación. Todas las rutas protegidas requieren un header `Authorization` con el formato:

```
Authorization: Bearer <token>
```

### Endpoints de Autenticación

#### POST /api/auth/login
Inicia sesión y obtiene un token JWT.

**Request Body:**
```json
{
  "usuario": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "usuario": "admin",
    "nombre_completo": "Administrador",
    "rol": "admin"
  }
}
```

#### POST /api/auth/refresh
Renueva un token de acceso usando un token de refresh.

## Gestión de Usuarios

### GET /api/usuarios
Obtiene lista de usuarios.

**Parámetros de Query:**
- `page` (int): Página actual (default: 1)
- `per_page` (int): Elementos por página (default: 10)
- `search` (string): Término de búsqueda

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "usuario": "admin",
      "nombre_completo": "Administrador del Sistema",
      "email": "admin@example.com",
      "rol": "admin",
      "activo": true,
      "fecha_creacion": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

### POST /api/usuarios
Crea un nuevo usuario.

**Request Body:**
```json
{
  "usuario": "nuevo_usuario",
  "password": "password123",
  "nombre_completo": "Nuevo Usuario",
  "email": "usuario@example.com",
  "rol": "usuario"
}
```

### PUT /api/usuarios/{id}
Actualiza un usuario existente.

### DELETE /api/usuarios/{id}
Elimina un usuario.

## Gestión de Países

### GET /api/paises
Obtiene lista de países.

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Paraguay",
    "codigo": "PY",
    "activo": true
  }
]
```

### POST /api/paises
Crea un nuevo país.

**Request Body:**
```json
{
  "nombre": "Brasil",
  "codigo": "BR"
}
```

## Gestión de Ciudades

### GET /api/ciudades
Obtiene lista de ciudades con filtros opcionales.

**Parámetros de Query:**
- `pais_id` (int): Filtrar por país
- `search` (string): Buscar por nombre

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Asunción",
    "pais_id": 1,
    "pais": {
      "id": 1,
      "nombre": "Paraguay",
      "codigo": "PY"
    },
    "activo": true
  }
]
```

### POST /api/ciudades
Crea una nueva ciudad.

**Request Body:**
```json
{
  "nombre": "Ciudad del Este",
  "pais_id": 1
}
```

## Gestión de Transportadoras

### GET /api/transportadoras
Obtiene lista de transportadoras.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "razon_social": "Transportes Rápidos S.A.",
      "ruc": "800123456-7",
      "direccion": "Av. Principal 123",
      "telefono": "+595 21 123456",
      "email": "contacto@transportesrapidos.com.py",
      "activo": true,
      "fecha_creacion": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /api/transportadoras
Crea una nueva transportadora.

**Request Body:**
```json
{
  "razon_social": "Nueva Transportadora S.A.",
  "ruc": "800987654-3",
  "direccion": "Nueva Dirección 456",
  "telefono": "+595 21 987654",
  "email": "contacto@nueva.com.py"
}
```

## Gestión de Remitentes

### GET /api/remitentes
Obtiene lista de remitentes.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "razon_social": "Empresa XYZ S.A.",
      "ruc": "800456789-0",
      "direccion": "Dirección del Remitente",
      "telefono": "+595 21 456789",
      "email": "contacto@empresa.com.py",
      "activo": true
    }
  ],
  "total": 1
}
```

## Gestión de Monedas

### GET /api/monedas
Obtiene lista de monedas disponibles.

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Guaraní",
    "codigo": "PYG",
    "simbolo": "₲",
    "activo": true
  },
  {
    "id": 2,
    "nombre": "Dólar Americano",
    "codigo": "USD",
    "simbolo": "$",
    "activo": true
  }
]
```

## Gestión de CRTs (Cartas de Porte)

### GET /api/crts
Obtiene lista de CRTs con filtros avanzados.

**Parámetros de Query:**
- `page` (int): Página
- `per_page` (int): Elementos por página
- `estado` (string): Filtrar por estado
- `fecha_desde` (date): Fecha desde
- `fecha_hasta` (date): Fecha hasta
- `transportadora_id` (int): Filtrar por transportadora
- `remitente_id` (int): Filtrar por remitente

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "numero_crt": "CRT-001-2024",
      "fecha_emision": "2024-01-15T10:00:00Z",
      "estado": "EMITIDO",
      "transportadora": {
        "id": 1,
        "razon_social": "Transportes Rápidos S.A."
      },
      "remitente": {
        "id": 1,
        "razon_social": "Empresa XYZ S.A."
      },
      "origen": {
        "id": 1,
        "nombre": "Asunción"
      },
      "destino": {
        "id": 2,
        "nombre": "Ciudad del Este"
      },
      "valor_incoterm": 15000.00,
      "moneda": {
        "id": 2,
        "codigo": "USD",
        "simbolo": "$"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

### POST /api/crts
Crea una nueva CRT.

**Request Body:**
```json
{
  "transportadora_id": 1,
  "remitente_id": 1,
  "origen_id": 1,
  "destino_id": 2,
  "valor_incoterm": 15000.00,
  "moneda_id": 2,
  "descripcion_mercaderia": "Productos electrónicos",
  "peso_bruto": 500.00,
  "volumen": 2.5
}
```

### GET /api/crts/{id}
Obtiene detalles de una CRT específica.

### PUT /api/crts/{id}
Actualiza una CRT existente.

### DELETE /api/crts/{id}
Elimina una CRT.

### GET /api/crts/estados
Obtiene lista de estados disponibles para CRTs.

**Response:**
```json
[
  "BORRADOR",
  "EMITIDO",
  "EN_TRANSITO",
  "ENTREGADO",
  "CANCELADO"
]
```

## Gestión de Honorarios

### GET /api/honorarios
Obtiene lista de honorarios.

**Parámetros de Query:**
- `transportadora_id` (int): Filtrar por transportadora
- `fecha_desde` (date): Fecha desde
- `fecha_hasta` (date): Fecha hasta

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "transportadora_id": 1,
      "transportadora": {
        "id": 1,
        "razon_social": "Transportes Rápidos S.A."
      },
      "monto": 2500.00,
      "moneda_id": 2,
      "moneda": {
        "id": 2,
        "codigo": "USD"
      },
      "fecha": "2024-01-15T00:00:00Z",
      "descripcion": "Pago por transporte CRT-001-2024",
      "estado": "PENDIENTE"
    }
  ],
  "total": 1
}
```

### POST /api/honorarios
Crea un nuevo registro de honorarios.

**Request Body:**
```json
{
  "transportadora_id": 1,
  "monto": 2500.00,
  "moneda_id": 2,
  "fecha": "2024-01-15",
  "descripcion": "Pago por transporte",
  "estado": "PENDIENTE"
}
```

## Reportes y Background Jobs

### POST /api/background-reports/create
Crea un reporte en background.

**Request Body:**
```json
{
  "report_type": "crt_summary",
  "parameters": {
    "date_from": "2024-01-01",
    "date_to": "2024-01-31"
  }
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "report_crt_summary_20240115_143022",
  "message": "Reporte en cola de procesamiento"
}
```

### GET /api/background-reports/status/{job_id}
Obtiene el estado de un reporte.

**Response:**
```json
{
  "status": "completed",
  "progress": 100,
  "message": "Reporte completado exitosamente",
  "created_at": "2024-01-15T14:30:22Z",
  "completed_at": "2024-01-15T14:30:25Z",
  "result": {
    "total_crts": 25,
    "total_valor": 375000.00,
    "por_estado": {
      "EMITIDO": 20,
      "ENTREGADO": 5
    }
  }
}
```

### GET /api/background-reports/active
Obtiene reportes activos.

### POST /api/background-reports/cancel/{job_id}
Cancela un reporte en proceso.

### GET /api/background-reports/types
Obtiene tipos de reportes disponibles.

**Response:**
```json
{
  "crt_summary": {
    "name": "Resumen de CRTs",
    "description": "Reporte completo con estadísticas de CRTs por período",
    "parameters": {
      "date_from": {"type": "date", "required": false},
      "date_to": {"type": "date", "required": false}
    }
  },
  "financial": {
    "name": "Reporte Financiero",
    "description": "Análisis financiero de honorarios y pagos",
    "parameters": {
      "date_from": {"type": "date", "required": false},
      "date_to": {"type": "date", "required": false}
    }
  },
  "activity": {
    "name": "Reporte de Actividad",
    "description": "Estadísticas generales de actividad del sistema",
    "parameters": {
      "days": {"type": "number", "required": false, "default": 30}
    }
  }
}
```

## Monitoreo y Métricas

### GET /api/health
Verifica el estado del sistema.

**Response:**
```json
{
  "status": "ok",
  "message": "Sistema Logístico CRT/MIC funcionando correctamente",
  "version": "2.0",
  "endpoints": {
    "crts": "/api/crts",
    "transportadoras": "/api/transportadoras",
    "remitentes": "/api/remitentes",
    "monedas": "/api/monedas",
    "paises": "/api/paises",
    "ciudades": "/api/ciudades"
  }
}
```

### GET /metrics
Obtiene métricas de Prometheus para monitoreo.

## Códigos de Estado HTTP

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Datos de solicitud inválidos
- `401 Unauthorized`: Token de autenticación faltante o inválido
- `403 Forbidden`: Permisos insuficientes
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto con el estado actual del recurso
- `422 Unprocessable Entity`: Datos válidos pero no procesables
- `500 Internal Server Error`: Error interno del servidor

## Manejo de Errores

Todos los errores siguen el formato estándar:

```json
{
  "error": "Descripción del error",
  "message": "Mensaje detallado del error",
  "details": {
    "campo": "Error específico del campo"
  }
}
```

## Rate Limiting

La API implementa rate limiting para prevenir abuso:
- 1000 requests por hora para usuarios autenticados
- 100 requests por hora para usuarios no autenticados

## Versionado

La API utiliza versionado en la URL:
- Versión actual: v1 (incluida en el base path)

## Webhooks y Notificaciones

El sistema soporta webhooks para eventos importantes:
- Creación de CRT
- Cambio de estado de CRT
- Procesamiento de honorarios

Los webhooks deben configurarse contactando al administrador del sistema.

## Logs y Auditoría

Todas las operaciones importantes son registradas para auditoría:
- Creación/modificación/eliminación de CRTs
- Cambios de estado
- Operaciones de usuarios
- Errores del sistema

## Soporte y Contacto

Para soporte técnico o preguntas sobre la API:
- Email: soporte@sistemalogistico.com.py
- Documentación completa: [URL de documentación interactiva]
- Estado del sistema: [URL de status page]