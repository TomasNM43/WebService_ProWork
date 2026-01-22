# Guía de Despliegue en IIS

## Requisitos Previos

1. **Windows Server** con IIS instalado
2. **Python 3.11** o superior instalado
3. **Oracle Instant Client** instalado y configurado
4. **CGI** y **FastCGI** habilitados en IIS

## Pasos de Instalación

### 1. Instalar Componentes de IIS

Abrir PowerShell como Administrador y ejecutar:

```powershell
# Instalar IIS con CGI
Install-WindowsFeature -name Web-Server -IncludeManagementTools
Install-WindowsFeature -name Web-CGI
```

### 2. Instalar Python y Dependencias

```powershell
# Navegar al directorio del proyecto
cd C:\inetpub\wwwroot\WebService_ProWork

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Habilitar wfastcgi
wfastcgi-enable
```

### 3. Configurar Oracle Instant Client

1. Descargar Oracle Instant Client desde [Oracle Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
2. Extraer en `C:\oracle\instantclient_19_x`
3. Agregar al PATH del sistema:

```powershell
$env:PATH += ";C:\oracle\instantclient_19_x"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::Machine)
```

### 4. Configurar IIS

1. Abrir **Administrador de IIS**
2. Crear un nuevo sitio web o aplicación:
   - **Nombre**: WebService_ProWork
   - **Ruta física**: `C:\inetpub\wwwroot\WebService_ProWork`
   - **Puerto**: 2025 (o el deseado)

3. Configurar el Application Pool:
   - Click derecho en el sitio → **Configuración básica** → **Grupo de aplicaciones**
   - Crear o modificar Application Pool:
     - **Versión de .NET CLR**: Sin código administrado
     - **Modo de canalización**: Integrado
     - **Identidad**: ApplicationPoolIdentity o cuenta de servicio

4. Permisos:
   - Click derecho en el sitio → **Editar permisos**
   - Agregar permisos de lectura/escritura a:
     - `IIS_IUSRS`
     - `IUSR`
     - Account del Application Pool

### 5. Actualizar web.config

Editar `web.config` y ajustar las rutas según tu instalación:

- Ruta de Python: `C:\Python311\python.exe` (ajustar según versión)
- Ruta de wfastcgi: `C:\Python311\Lib\site-packages\wfastcgi.py`
- PYTHONPATH: Ruta completa al proyecto
- WSGI_LOG: Ruta para logs

### 6. Crear Directorio de Logs

```powershell
New-Item -Path "C:\inetpub\wwwroot\WebService_ProWork\logs" -ItemType Directory
```

### 7. Verificar Configuración

1. Reiniciar el sitio en IIS
2. Probar acceso: `http://localhost:2025/`
3. Verificar logs en caso de error

## Estructura de Archivos

```
WebService_ProWork/
├── app.py                 # Aplicación Flask principal
├── constants.py           # Constantes de configuración
├── requirements.txt       # Dependencias Python
├── web.config            # Configuración IIS
├── logs/                 # Directorio de logs
└── venv/                 # Entorno virtual (opcional)
```

## Troubleshooting

### Error 500.0

- Verificar que Python esté correctamente instalado
- Verificar rutas en web.config
- Revisar logs en `C:\inetpub\wwwroot\WebService_ProWork\logs\wfastcgi.log`

### Error de Oracle

- Verificar que Oracle Instant Client esté en el PATH
- Verificar conectividad a la base de datos
- Revisar credenciales en `constants.py`

### Permisos

- Asegurarse que IIS_IUSRS tenga permisos en el directorio
- Verificar permisos del Application Pool

## Configuración de Producción

1. Cambiar `debug=False` en app.py
2. Usar variables de entorno para credenciales
3. Implementar logging apropiado
4. Configurar SSL/HTTPS
5. Implementar límites de tasa (rate limiting)

## Comandos Útiles

```powershell
# Reiniciar IIS
iisreset

# Ver logs de IIS
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 50

# Verificar wfastcgi
wfastcgi-enable

# Listar sitios IIS
Get-IISSite
```
