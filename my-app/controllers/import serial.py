import serial
import mysql.connector
from datetime import datetime

# Configurar el puerto serial (debes cambiar el nombre del puerto serial según tu sistema operativo)
puerto_serial = 'COM3'  # Linux
#puerto_serial = 'COM3'  # Windows

# Velocidad de comunicación (baud rate)
baud_rate = 9600

# Configuración de la conexión a la base de datos
config = {
  'user': 'root',
  'password': 'c-Fg46DD45HaFcf5da3-1Dcc1b6hABEG',
  'host': 'roundhouse.proxy.rlwy.net',
  'port': '51567',
  'database': 'railway',
}
try:
    # Abrir el puerto serial
    with serial.Serial(puerto_serial, baud_rate) as puerto:
        # Establecer conexión a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Leer datos del puerto serial hasta que se reciba una línea vacía
        while True:
            linea = puerto.readline().decode().strip()
            if linea:
                datos = linea.split(":")
                if datos[0] == "temp":
                    temperatura = float(datos[1])
                    estado_sistema = "Normal"  # Suponiendo que el sistema está en estado normal
                    hora_fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Insertar datos de temperatura en la tabla
                    insert_query = "INSERT INTO Sistema_de_temperatura (Temperatura_Ambiente, Estado_Sistema_Refrigeracion, Hora_Fecha) VALUES (%s, %s, %s)"
                    data = (temperatura, estado_sistema, hora_fecha)
                    cursor.execute(insert_query, data)
                    connection.commit()

                    print("Datos de temperatura insertados correctamente")

                elif datos[0] == "alertaTemp":
                    # Manejar la alerta de temperatura si es necesario
                    pass

                elif datos[0] == "UID de la tarjeta":
    # Código para obtener el ID de usuario y el nombre de usuario asociado al UID de la tarjeta
                        codigo_seguridad = datos[1]
                        query = "SELECT usuarios.id_usuario, usuarios.nombre_usuario FROM usuarios JOIN Sistema_Seguridad ON Sistema_Seguridad.Codigo_Seguridad = usuarios.id_usuario WHERE Sistema_Seguridad.Codigo_Seguridad = %s"
                        cursor.execute(query, (codigo_seguridad,))
                        usuario = cursor.fetchone()

                        if usuario:
                            id_usuario, nombre_usuario = usuario
                            codigo_seguridad = datos[1]  # No estoy seguro de por qué asignas datos[1] aquí, deberías revisar si es correcto
                            hora_fecha_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # Insertar datos de RFID en la tabla
                            insert_query = "INSERT INTO Sistema_Seguridad (Codigo_Seguridad, Id_Usuario, Nombre_Usuario, hora_fecha_Entrada) VALUES (%s, %s, %s, %s)"
                            data = (codigo_seguridad, id_usuario, nombre_usuario, hora_fecha_entrada)
                            cursor.execute(insert_query, data)
                            connection.commit()

                            print("Datos de RFID insertados correctamente")
                        else:
                            print("No se encontró usuario asociado al UID de la tarjeta")


                else:
                    print("Datos no reconocidos:", datos)
            else:
                break

except serial.SerialException as e:
    print("Error al abrir el puerto serial:", e)

except mysql.connector.Error as err:
    print("Error al conectar a la base de datos:", err)

except KeyboardInterrupt:
    print("Proceso interrumpido por el usuario")

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión a la base de datos cerrada")
