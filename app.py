import cx_Oracle
import sys
import os

from flask import Flask, jsonify, request
from constants import DB_USER, DB_PASSWORD, DSN, WEB_SERVICE_HOST, WEB_SERVICE_PORT

# Configuración para MacOS (Wilmar)
if sys.platform.startswith("darwin"):
    cx_Oracle.init_oracle_client(lib_dir="/Volumes/instantclient-basic-macos.x64-19.8.0.0.0dbru")
# cd /Volumes/instantclient-basic-macos.x64-19.8.0.0.0dbru
# ./install_ic.sh

# Configuración para Windows - Oracle Instant Client
if sys.platform.startswith("win"):
    oracle_client_path = r"C:\instantclient_19_29"
    if os.path.exists(oracle_client_path):
        try:
            cx_Oracle.init_oracle_client(lib_dir=oracle_client_path)
        except Exception as e:
            # Ya inicializado o en PATH
            pass

app = Flask(__name__)

def establecerConexion():
    """
    Establece conexión con base de datos
    """
    conexion = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN, encoding="UTF-8")
    return conexion

@app.route('/')
def indice():
    """
    Muestra mensaje de bienvenida en página principal
    """
    return("ProWorkAPI")

@app.route('/personal', methods=['POST'])
def validarCredenciales() -> jsonify:
    """
    Valida datos para inicio de sesión
    """
    try:
        conexion = establecerConexion()
    except Exception as e:
        return jsonify({'error': str(e), 'mensaje': "Error conectando a la base de datos", 'exito': False})
    
    personal = None
    asistencia = None
    
    try:
        data = request.get_json()
        if not data.get('ID_PERSONAL') or not data.get('ID_INSTITUCION') or not data.get('PASSWORD'):
            return jsonify({'mensaje': "Datos incompletos", 'exito': False})
        
        with conexion.cursor() as cursor:
            # Llamar al procedimiento para obtener datos personales
            cursor.callproc('PRO_WORK.PERSONALMOSTRAR', [data.get('ID_PERSONAL'), data.get('ID_INSTITUCION'), data.get('PASSWORD')])
            result_sets = iter(cursor.getimplicitresults())
            
            try:
                personal_result = next(result_sets)
                for row in personal_result:
                    personal = {'ID_PERSONAL': row[0],
                                'NOMBRE': row[1],
                                'APELLIDO_PATERNO': row[2],
                                'APELLIDO_MATERNO': row[3],
                                'CARGO': row[4],
                                'AREA': row[5],
                                'CORREO': row[6],
                                'TELEFONO': row[7],
                                'ID_TIPO_TRABAJADOR': row[8],
                                'ID_INSTITUCION': row[9]}
            except StopIteration:
                return jsonify({'mensaje': "No se encontraron datos personales", 'exito': False})
            
            # Llamar al procedimiento para obtener datos de asistencia
            cursor.callproc('PRO_WORK.ASISTENCIAVERIFICAR', [data.get('ID_PERSONAL')])
            result_sets = iter(cursor.getimplicitresults())
            
            try:
                asistencia_result = next(result_sets)
                for row in asistencia_result:
                    asistencia = {'FECHA_HORA_FIN_PRG': row[0]}
            except StopIteration:
                return jsonify({'mensaje': "No se encontraron datos de asistencia", 'exito': False})
            
            if personal and asistencia:
                return jsonify({'datos': personal, 'asistencia': asistencia, 'mensaje': "Ok", 'exito': True})
            else:
                return jsonify({'mensaje': "Datos incorrectos", 'exito': False})
    except Exception as e:
        return jsonify({'mensaje': "Error en el procedimiento: " + str(e), 'exito': False})

@app.route('/parametros/<ID_INSTITUCION>', methods=['GET'])
def listarParametrosPorInstitucion(ID_INSTITUCION: str) -> jsonify:
    """
    Listar tabla Parametros
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    parametros = None
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.INSTITUCION_PARAMETROMOSTRAR', [ID_INSTITUCION])
            for results in cursor.getimplicitresults():
                for row in results:
                    print(row)
                    parametros = {'VERIFICACION_EVENTO_MINUTOS': row[0],
                                  'HORA_INICIO_REFRIGERIO_PRG': row[1],
                                  'HORA_FIN_REFRIGERIO_PRG': row[2],
                                  'ACTUALIZACION_MINUTOS_IMPRODUCTIVOS': row[3],
                                  'VERIFICACION_PROGRAMA_MINUTOS': row[4],
                                  'VERIFICACION_AVANCE_MINUTOS': row[5]}
            if parametros:
                return jsonify({'datos': parametros, 'mensaje': "Ok", 'exito': True})
            else:
                return jsonify({'mensaje': "Error iniciando la aplicación", 'exito': False})
    except Exception:
        return jsonify({'mensaje': "Error con los datos", 'exito': False})

@app.route('/programas/<ID_PERSONAL>', methods=['GET'])
def listarProgramas(ID_PERSONAL: str) -> jsonify:
    """
    Listar tabla Programas
    """
    try:
        conexion = establecerConexion()
    except Exception as e:
        return jsonify({'error': str(e), 'mensaje': "Error conectando a la base de datos", 'exito': False})
    
    programas = []
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONA_HERRAMIENTASMOSTRAR', [ID_PERSONAL])
            for results in cursor.getimplicitresults():
                for row in results:
                    programas.append({'TIPO_HERRAMIENTA': row[0]})
            return jsonify({'datos': programas, 'mensaje': "Ok", 'exito': True})
    except Exception as e:
        return jsonify({'mensaje': "Error al recopilar datos", 'exito': False, 'error': str(e)})

@app.route('/asistencia/inicia', methods=['POST'])
def actualizarAsistenciaInicia() -> jsonify:
    """
    Establece hora inicio
    """
    data = request.get_json()
    ID_PERSONAL = data.get('ID_PERSONAL')
    print(ID_PERSONAL)
    if not ID_PERSONAL:
        return jsonify({'error': 'ID_PERSONAL es requerido', 'exito': False})

    try:
        conexion = establecerConexion()
    except Exception as e:
        return jsonify({'error': str(e), 'mensaje': "Error conectando a la base de datos", 'exito': False})
    
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.ASISTENCIAINICIAR', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception as e:
        return jsonify({'error': str(e), 'mensaje': "Error inicializando jornada", 'exito': False})
    finally:
        if conexion:
            conexion.close()

@app.route('/asistencia/finaliza/<ID_PERSONAL>', methods=['PUT'])
def actualizarAsistenciaFinaliza(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora fin
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.ASISTENCIAFINALIZAR', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error finalizando jornada", 'exito': False})

@app.route('/justifica/<ID_INSTITUCION>', methods=['GET'])
def listarJustifica(ID_INSTITUCION: str) -> jsonify:
    """
    Listar tabla Tipo_Justifica
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    justificaciones = []
    temp = None
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONA_JUSTIFICACIONMOSTRAR', [ID_INSTITUCION])
            for results in enumerate(cursor.getimplicitresults()):
                for row in results[1]:
                    temp = {'ID_JUSTIFICACION': row[0],
                            'DESCRIPCION': row[1],
                            'MINUTOS_JUSTIFICADOS': row[2]}
                    justificaciones.append(temp)
            return jsonify({'datos': justificaciones, 'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error al recopilar datos", 'exito': False})

@app.route('/evento', methods=['POST'])
def grabarEvento() -> jsonify:
    """
    Crea evento
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})

    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONAL_EVENTO_DIAGUARDAR', list(request.json.values()))
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception as e:
        print(e)
        return jsonify({'mensaje': "Error al grabar evento", 'exito': False})

@app.route('/minutos/improductivos/<ID_PERSONAL>/<VALOR>', methods=['PUT'])
def actualizarMinutosImproductivos(ID_PERSONAL:str, VALOR: int) -> jsonify:
    """
    Actualiza minutos improductvos establecidos en parametros
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.ACTUALIZAMINUTOSIMPRODUCTIVOS', [ID_PERSONAL, VALOR])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error actualizando minutos improductivos", 'exito': False})

@app.route('/refrigerio/inicia/<ID_PERSONAL>', methods=['PUT'])
def actualizarRefrigerioInicia(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora inicio de refrigerio
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.REFRIGERIOSALIDA', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "No existe refrigerio para iniciar", 'exito': False})

@app.route('/refrigerio/finaliza/<ID_PERSONAL>', methods=['PUT'])
def actualizarRefrigerioFinaliza(ID_PERSONAL: str) -> jsonify:
    """
    Establece hora fin de refrigerio
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.REFRIGERIOREGRESO', [ID_PERSONAL])
            conexion.commit()
            return jsonify({'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "No existe refrigerio para finalizar", 'exito': False})

@app.route('/actividades/<ID_PERSONAL>', methods=['GET'])
def listarActividades(ID_PERSONAL: str) -> jsonify:
    """
    Listar actividades
    """
    try:
        conexion = establecerConexion()
    except Exception:
        return jsonify({'error': conexion, 'mensaje': "Error conectando a la base de datos", 'exito': False})
    actividades = []
    temp = None
    try:
        with conexion.cursor() as cursor:
            cursor.callproc('PRO_WORK.PERSONAL_ACTIVIDADMOSTRAR', [ID_PERSONAL])
            for results in enumerate(cursor.getimplicitresults()):
                for row in results[1]:
                    temp = {'TITULO_ACTIVIDAD': row[0],
                            'DESCRIPCION_ACTIVIDAD': row[1],
                            'ESTADO_ACTIVIDAD': row[2],
                            'AVANCE_ACTIVIDAD': row[3]}
                    actividades.append(temp)
            return jsonify({'datos': actividades, 'mensaje': "Ok", 'exito': True})
    except Exception:
        return jsonify({'mensaje': "Error al recopilar datos", 'exito': False})

if __name__ == '__main__':
    # Para desarrollo local
    app.run(host=WEB_SERVICE_HOST, port=WEB_SERVICE_PORT, debug=True)
    # Para producción en IIS, comentar la línea anterior y descomentar la siguiente:
    # app.run(debug=False)