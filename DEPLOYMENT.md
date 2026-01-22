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

# Instalar dependencias (NO usar entorno virtual para IIS)
pip install -r requirements.txt

# Habilitar wfastcgi y GUARDAR LA SALIDA
wfastcgi-enable
```

**IMPORTANTE**: Copia la ruta completa que devuelve `wfastcgi-enable`. Será algo como:
```
"C:\Python311\python.exe|C:\Python311\Lib\site-packages\wfastcgi.py"
```
Esta ruta será necesaria para el siguiente paso.

### 3. Configurar Oracle Instant Client

1. Descargar Oracle Instant Client desde [Oracle Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
2. Extraer en `C:\oracle\instantclient_19_x`
3. Agregar al PATH del sistema:

```powershell
$env:PATH += ";C:\oracle\instantclient_19_x"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::Machine)
```

### 4. Configurar FastCGI en IIS (CRÍTICO)

```powershell
# Ejecutar como Administrador en PowerShell
cd $env:windir\system32\inetsrv

# Agregar la aplicación FastCGI con la ruta obtenida de wfastcgi-enable
.\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='C:\Python311\python.exe',arguments='C:\Python311\Lib\site-packages\wfastcgi.py',maxInstances='4',idleTimeout='1800',activityTimeout='30',requestTimeout='90',instanceMaxRequests='10000',protocol='NamedPipe',flushNamedPipe='False']" /commit:apphost
```

**IMPORTANTE**: Reemplaza las rutas de Python según tu instalación. Usa las rutas exactas que obtuviste de `wfastcgi-enable`.

### 5. Crear Sitio en IIS

1. Abrir **Administrador de IIS**
2. Crear un nuevo sitio web:
   - **Nombre**: WebService_ProWork
   - **Ruta física**: `C:\inetpub\wwwroot\WebService_ProWork`
   - **Puerto**: 10005

3. Configurar el Application Pool:
   - Click derecho en el sitio → **Configuración básica** → **Grupo de aplicaciones**
   - Crear o modificar Application Pool:
     - **Nombre**: WebService_ProWork_Pool
     - **Versión de .NET CLR**: Sin código administrado
     - **Modo de canalización**: Integrado
     - **Identidad**: ApplicationPoolIdentity

4. Permisos del directorio:
   
```powershell
# Dar permisos al directorio del proyecto
icacls "C:\inetpub\wwwroot\WebService_ProWork" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "C:\inetpub\wwwroot\WebService_ProWork" /grant "IUSR:(OI)(CI)F" /T
icacls "C:\inetpub\wwwroot\WebService_ProWork\logs" /grant "IIS_IUSRS:(OI)(CI)F" /T
```

### 6. Actualizar web.config

Editar `web.config` y ajustar con la ruta EXACTA obtenida de `wfastcgi-enable`:

```xml
<handlers>
  <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" 
       scriptProcessor="C:\Python311\python.exe|C:\Python311\Lib\site-packages\wfastcgi.py" 
       resourceType="Unspecified" requireAccess="Script" />
</handlers>
```

Y verificar que `PYTHONPATH` y `WSGI_LOG` tengan las rutas correctas:

```xml
<appSettings>
  <add key="PYTHONPATH" value="C:\inetpub\wwwroot\WebService_ProWork" />
  <add key="WSGI_HANDLER" value="app.app" />
  <add key="WSGI_LOG" value="C:\inetpub\wwwroot\WebService_ProWork\logs\wfastcgi.log" />
</appSettings>
```

### 7. Verificar Configuración

```powershell
# Reiniciar IIS
iisreset

# Verificar que FastCGI esté configurado correctamente
cd $env:windir\system32\inetsrv
.\appcmd.exe list config -section:system.webServer/fastCgi

# Probar acceso
Start-Process "http://localhost:10005/"
```

Si todo está correcto, deberías ver "ProWorkAPI" en el navegador.

### 8. Verificar Logs

Si hay errores, revisar:
- `C:\inetpub\wwwroot\WebService_ProWork\logs\wfastcgi.log`
- Visor de eventos de Windows (Event Viewer)
- Logs de IIS en `C:\inetpub\logs\LogFiles\`

## Estructura de Archivos

```
WebService_ProW - "No se pudo encontrar handler scriptProcessor"

Este es el error más común. Solución:

1. **Obtener la ruta correcta de wfastcgi:**
```powershell
wfastcgi-enable
```

2. **Configurar FastCGI en IIS manualmente:**
```powershell
cd $env:windir\system32\inetsrv

# Listar configuraciones actuales
.\appcmd.exe list config -section:system.webServer/fastCgi

# Si no existe, agregar (reemplazar rutas según tu sistema):
.\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='C:\Python311\python.exe',arguments='C:\Python311\Lib\site-packages\wfastcgi.py']" /commit:apphost
```

3. **Actualizar web.config con la ruta exacta:**
- Abrir `web.config`
- Encontrar la línea `scriptProcessor=`
- Reemplazar con la ruta completa que devolvió `wfastcgi-enable`

4. **Reiniciar IIS:**
```powershell
iisreset
```

### Error 500.0 - Otros casos

- Verificar que Python esté en el PATH del sistema
- Verificar rutas en web.config (sin espacios extras)
- Revisar logs en `C:\inetpub\wwwroot\WebService_ProWork\logs\wfastcgi.log`
- Verificar permisos NTFS en el directorio del proyecto

### Error de Oracle

- Verificar que Oracle Instant Client esté en el PATH del sistema
- Reiniciar IIS después de agregar Oracle al PATH
- Verificar conectividad: `tnsping 192.168.18.8:1521/orcl`
- Revisar credenciales en `constants.py`

### Permisos

```powershell
# Verificar y corregir permisos
icacls "C:\inetpub\wwwroot\WebService_ProWork" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "C:\inetpub\wwwroot\WebService_ProWork" /grant "IUSR:(OI)(CI)F" /T
```

### El sitio no responde

- Verificar que el puerto 10005 no esté en uso:
```powershell
netstat -ano | findstr :10005
```
- Verificar firewall de Windows
- Comprobar que el sitio esté iniciado en IISService_ProWork\logs\wfastcgi.log`

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
