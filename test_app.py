"""
Script de diagnóstico para verificar que todo funcione antes de IIS
"""
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")

# Test 1: Importar Flask
try:
    from flask import Flask
    print("✓ Flask OK")
except Exception as e:
    print(f"✗ Error Flask: {e}")
    sys.exit(1)

# Test 2: Importar cx_Oracle
try:
    import cx_Oracle
    print("✓ cx_Oracle OK")
    print(f"  Versión cx_Oracle: {cx_Oracle.__version__}")
except Exception as e:
    print(f"✗ Error cx_Oracle: {e}")
    print("\nSOLUCIÓN:")
    print("1. Descarga Oracle Instant Client desde:")
    print("   https://www.oracle.com/database/technologies/instant-client/downloads.html")
    print("2. Extrae en C:\\oracle\\instantclient_XX_X")
    print("3. Agrega al PATH del sistema")
    sys.exit(1)

# Test 3: Cargar constants
try:
    from constants import DB_USER, DB_PASSWORD, DSN
    print("✓ constants.py OK")
    print(f"  DSN: {DSN}")
except Exception as e:
    print(f"✗ Error constants: {e}")
    sys.exit(1)

# Test 4: Importar app
try:
    from app import app
    print("✓ app.py OK")
except Exception as e:
    print(f"✗ Error app.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Intentar conexión a BD (opcional, comentado por defecto)
# try:
#     import cx_Oracle
#     conn = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN)
#     print("✓ Conexión a BD OK")
#     conn.close()
# except Exception as e:
#     print(f"⚠ Advertencia conexión BD: {e}")

print("\n✓✓✓ Todos los tests pasaron! El problema puede ser de permisos IIS.")
print("\nPróximos pasos:")
print("1. Ejecuta: icacls 'C:\\inetpub\\wwwroot\\WebService_ProWork' /grant 'IIS_IUSRS:(OI)(CI)F' /T")
print("2. Ejecuta: iisreset")
print("3. Revisa Event Viewer (eventvwr.msc) > Windows Logs > Application")
