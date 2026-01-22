# WebService ProWork

API REST para gestión de asistencias y actividades del personal.

## Estructura del Proyecto

```
WebService_ProWork/
├── app.py                      # Aplicación Flask principal
├── constants.py                # Constantes de configuración (DB)
├── requirements.txt            # Dependencias Python
├── web.config                  # Configuración para IIS
├── DEPLOYMENT.md              # Guía de despliegue en IIS
├── .gitignore                 # Archivos ignorados por git
│
├── config/                    # Configuraciones adicionales
│   └── __init__.py
│
├── routes/                    # Endpoints organizados por módulo
│   └── __init__.py
│
├── utils/                     # Funciones auxiliares y helpers
│   └── __init__.py
│
├── static/                    # Archivos estáticos
│   ├── css/                  # Hojas de estilo
│   ├── js/                   # Scripts JavaScript
│   └── images/               # Imágenes
│
├── templates/                 # Templates HTML (si se requieren)
│
└── logs/                      # Logs de la aplicación
    └── .gitkeep
```

## Endpoints Disponibles

### Autenticación
- `POST /personal` - Validar credenciales

### Parámetros
- `GET /parametros/<ID_INSTITUCION>` - Obtener parámetros por institución

### Programas/Herramientas
- `GET /programas/<ID_PERSONAL>` - Listar programas de un usuario

### Asistencia
- `POST /asistencia/inicia` - Iniciar jornada
- `PUT /asistencia/finaliza/<ID_PERSONAL>` - Finalizar jornada

### Refrigerio
- `PUT /refrigerio/inicia/<ID_PERSONAL>` - Iniciar refrigerio
- `PUT /refrigerio/finaliza/<ID_PERSONAL>` - Finalizar refrigerio

### Justificaciones
- `GET /justifica/<ID_INSTITUCION>` - Listar tipos de justificación

### Eventos
- `POST /evento` - Crear evento

### Minutos Improductivos
- `PUT /minutos/improductivos/<ID_PERSONAL>/<VALOR>` - Actualizar minutos

### Actividades
- `GET /actividades/<ID_PERSONAL>` - Listar actividades del personal

## Requisitos

- Python 3.11+
- Oracle Database
- Oracle Instant Client
- IIS (para producción en Windows Server)

## Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos en constants.py
# Ejecutar aplicación
python app.py
```

La aplicación estará disponible en `http://localhost:2025`

## Despliegue en IIS

Consultar [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones detalladas.

## Tecnologías

- **Flask** - Framework web
- **cx_Oracle** - Conector Oracle Database
- **wfastcgi** - FastCGI para IIS

## Configuración

Las credenciales de base de datos se encuentran en `constants.py`:
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- DB_SERVICE

## Desarrollo

Para desarrollo local, mantener `debug=True` en app.py.
Para producción, cambiar a `debug=False`.
