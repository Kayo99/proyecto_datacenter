# Importandopaquetes desde flask
from flask import session, flash

# Importando conexion a BD
from conexion.conexionBD import connectionBD
# Para  validar contraseña
from werkzeug.security import check_password_hash

import re
# Para encriptar contraseña generate_password_hash
from werkzeug.security import generate_password_hash


def recibeInsertRegisterUser(cedula, name, surname, id_area, id_rol, pass_user, Estado_civil, Edad):
    respuestaValidar = validarDataRegisterLogin(
        cedula, name, surname, pass_user,Estado_civil, Edad)

    if (respuestaValidar):
        nueva_password = generate_password_hash(pass_user, method='scrypt')
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = """
                    INSERT INTO usuarios(cedula, nombre_usuario, apellido_usuario, id_area, id_rol, password, Estado_civil, Edad) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (cedula, name, surname, id_area, id_rol, nueva_password, Estado_civil, Edad)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert
        except Exception as e:
            print(f"Error en el Insert users: {e}")
            return []
    else:
        return False


# Validando la data del Registros para el login
def validarDataRegisterLogin(cedula, name, surname, pass_user,Estado_civil,Edad):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM usuarios WHERE cedula = %s"
                cursor.execute(querySQL, (cedula,))
                userBD = cursor.fetchone()  # Obtener la primera fila de resultados

                if userBD is not None:
                    flash('el registro no fue procesado ya existe la cuenta', 'error')
                    return False
                elif not cedula or not name or not pass_user:
                    flash('por favor llene los campos del formulario.', 'error')
                    return False
                else:
                    # La cuenta no existe y los datos del formulario son válidos, puedo realizar el Insert
                    return True
    except Exception as e:
        print(f"Error en validarDataRegisterLogin : {e}")
        return []


def info_perfil_session(id):
    print(id)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_usuario, nombre_usuario, apellido_usuario, cedula, id_area, id_rol, Estado_civil, Edad FROM usuarios WHERE id_usuario = %s"
                cursor.execute(querySQL, (id,))
                info_perfil = cursor.fetchall()
        return info_perfil
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []

def info_temperatura_session(id):
    print(id)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT Id, Temperatura_Ambiente, Estado_Sistema_Refrigeracion,Hora_Fecha FROM Sistema_de_temperatura"
                cursor.execute(querySQL, (id,))
                info_temperatura = cursor.fetchall()
        return info_temperatura
    except Exception as e:
        print(f"Error en info_temperatura_session : {e}")
        return []

def info_humo_session(id):
    print(id)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT Id, Marca, Estado, Alerta, Descripcion_Sis_In, id_monitoreo, Hora_Fecha, Estado_sistema_contra_incendios FROM Sistema_contra_incendios"
                cursor.execute(querySQL, (id,))
                info_humo = cursor.fetchall()
        return info_humo
    except Exception as e:
        print(f"Error en info_humo_session : {e}")
        return []

def info_ventilacion_session(id):
    print(id)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT Codigo_Ventilacion, Estado_Ventilacion,Hora_Fecha_Ventilacion FROM Registro_de_Ventilacion"
                cursor.execute(querySQL, (id,))
                info_ventilacion = cursor.fetchall()
        return info_ventilacion
    except Exception as e:
        print(f"Error en info_ventilacion_session : {e}")
        return []
    
def procesar_update_perfil(data_form,id):
    # Extraer datos del diccionario data_form
    id_user = id
    cedula = data_form['cedula']
    nombre_usuario = data_form['name']
    apellido_usuario = data_form['surname']
    id_area = data_form['selectArea']
    id_rol= data_form['selectRol']
    Estado_civil= data_form['Estado_civil']
    Edad= data_form['Edad']

    new_pass_user = data_form['new_pass_user']
    

    if session['rol'] == 1 :
        try:
            nueva_password = generate_password_hash(
                new_pass_user, method='scrypt')
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    querySQL = """
                        UPDATE usuarios
                        SET 
                            nombre_usuario = %s,
                            apellido_usuario = %s,
                            id_area = %s,
                            id_rol = %s,
                            Estado_civil = %s,
                            Edad = %s,
                            password = %s
                        WHERE id_usuario = %s
                    """
                    params = (nombre_usuario,apellido_usuario, id_area, id_rol,Estado_civil,Edad,
                                nueva_password,id_user)
                    cursor.execute(querySQL, params)
                    conexion_MySQLdb.commit()
            return 1
        except Exception as e:
            print(
                f"Ocurrió en procesar_update_perfil: {e}")
            return []
    
    pass_actual = data_form['pass_actual']
    repetir_pass_user = data_form['repetir_pass_user']

    print(id_area+" HOLA "+id_rol)

    if not pass_actual and not new_pass_user and not repetir_pass_user:
            return updatePefilSinPass(id_user, nombre_usuario, apellido_usuario, id_area, id_rol, Estado_civil, Edad)

    with connectionBD() as conexion_MySQLdb:
        with conexion_MySQLdb.cursor(dictionary=True) as cursor:
            querySQL = """SELECT * FROM usuarios WHERE cedula = %s LIMIT 1"""
            cursor.execute(querySQL, (cedula,))
            account = cursor.fetchone()
            if account:
                
                if check_password_hash(account['password'], pass_actual):
                    # Verificar si new_pass_user y repetir_pass_user están vacías
                        if new_pass_user != repetir_pass_user:
                            return 2
                        else:
                            try:
                                nueva_password = generate_password_hash(
                                    new_pass_user, method='scrypt')
                                with connectionBD() as conexion_MySQLdb:
                                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                                        querySQL = """
                                            UPDATE usuarios
                                            SET 
                                                nombre_usuario = %s,
                                                apellido_usuario = %s,
                                                id_area = %s,
                                                Estado_civil = %s,
                                                Edad = %s,
                                                password = %s
                                            WHERE id_usuario = %s
                                        """
                                        params = (nombre_usuario,apellido_usuario,id_area,
                                                  nueva_password,Estado_civil,Edad,id_user)
                                        cursor.execute(querySQL, params)
                                        conexion_MySQLdb.commit()
                                return cursor.rowcount or []
                            except Exception as e:
                                print(
                                    f"Ocurrió en procesar_update_perfil: {e}")
                                return []
            else:
                return 0



def updatePefilSinPass(id_user, nombre_usuario, apellido_usuario, id_area, id_rol, Estado_civil, Edad):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    UPDATE usuarios
                    SET 
                        nombre_usuario = %s,
                        apellido_usuario = %s,
                        id_area = %s,
                        id_rol = %s,
                        Estado_civil = %s,
                        Edad = %s
                    WHERE id_usuario = %s
                """
                params = ( nombre_usuario, apellido_usuario, id_area, id_rol,Estado_civil, Edad, id_user)
                cursor.execute(querySQL, params)
                conexion_MySQLdb.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Ocurrió un error en la funcion updatePefilSinPass: {e}")
        return []


def dataLoginSesion():
    inforLogin = {
        "id": session['id'],
        "name": session['name'],
        "cedula": session['cedula'],
        "rol": session['rol']
    }
    return inforLogin
