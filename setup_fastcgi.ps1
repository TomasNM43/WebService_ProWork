# Script para configurar FastCGI correctamente con Oracle
# Ejecutar como Administrador

$pythonPath = "C:\inetpub\wwwroot\WebService_ProWork\.venv\Scripts\python.exe"
$wfastcgiPath = "C:\inetpub\wwwroot\WebService_ProWork\.venv\Lib\site-packages\wfastcgi.py"
$oraclePath = "C:\instantclient_19_29"

Write-Host "Configurando FastCGI..." -ForegroundColor Yellow

# Limpiar configuración existente
cd $env:windir\system32\inetsrv
.\appcmd.exe clear config -section:system.webServer/fastCgi

# Agregar con variables de entorno
.\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='$pythonPath',arguments='$wfastcgiPath',maxInstances='4']" /commit:apphost

# Agregar variable de entorno PATH con Oracle
.\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='$pythonPath',arguments='$wfastcgiPath'].environmentVariables.[name='PATH',value='$oraclePath;%PATH%']" /commit:apphost

# Agregar variable TNS_ADMIN si tienes tnsnames.ora
# .\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='$pythonPath',arguments='$wfastcgiPath'].environmentVariables.[name='TNS_ADMIN',value='$oraclePath']" /commit:apphost

Write-Host "FastCGI configurado. Reiniciando IIS..." -ForegroundColor Green
iisreset

Write-Host "Configuración completa. Verifica en:" -ForegroundColor Green
Write-Host "  http://localhost:10005/" -ForegroundColor Cyan
