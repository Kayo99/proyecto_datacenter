import serial
import mysql.connector
from datetime import datetime
import time

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
#----------------------------------------------------------------------------------------------- desde aqui empieza el codigo 
        # Leer datos del puerto serial hasta que se reciba una línea vacía
        while True:
            linea = puerto.readline().decode().strip()
            if linea:
                datos = linea.split(":")
                
 # ------------------------------------------------------------------------------------------- Toma de datos de temperatura               
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

#------------------------------------------------------------------------------------------------ Fin de toma de datos de temperatura
                
#------------------------------------------------------------------------------------------------ Inicio de toma de valores de incendio

                elif datos[0] == "Humo":
                    valorMQ = int(datos[1])
                    if valorMQ > 500:
                        print("Humo detectado:", valorMQ)
                        # Aquí puedes agregar el código para manejar el humo, como enviar una alerta, etc.
                        humo=valorMQ
                        insert_query = "INSERT INTO Sistema_contra_incendios (Humo, Estado_sistema_contra_incendios) VALUES (%s, %s)"
                        data = (humo, 'Alerta Incendio')
                        cursor.execute(insert_query, data)
                        connection.commit()
                         
                        print("Datos Contra Incedios insertados correctamente")

#---------------------------------------------------------------------------------------------- Inicio de insertar la tarjeta
                elif "UID de la tarjeta:" in linea:
                    codigo_tarjeta = linea.split(":")[1].strip()
                    print("Código de la tarjeta RFID detectada:", codigo_tarjeta)

                    # Consultar si la tarjeta está autorizada
                    query = "SELECT COUNT(*) FROM Tarjetas WHERE numero_tarjeta = %s"
                    cursor.execute(query, (codigo_tarjeta,))
                    count = cursor.fetchone()[0]

                    if count == 0:
                        # Obtener el ID de usuario manualmente
                        id_usuario = input("Ingrese el ID de usuario asociado a la tarjeta: ")

                        # Insertar los datos en la tabla Tarjetas
                        query_insert = "INSERT INTO Tarjetas (numero_tarjeta, id_usuario) VALUES (%s, %s)"
                        cursor.execute(query_insert, (codigo_tarjeta, id_usuario))
                        connection.commit()

                        print("Datos de la tarjeta insertados correctamente.")

                    elif count > 0:
                        print("Acceso al data center concedido")

                        # Obtener la ID de la tarjeta asociada al número de tarjeta
                        query_tarjeta = "SELECT id_tarjeta FROM Tarjetas WHERE numero_tarjeta = %s"
                        cursor.execute(query_tarjeta, (codigo_tarjeta,))
                        tarjeta = cursor.fetchone()

                        if tarjeta:
                            id_tarjeta = tarjeta[0]

                            # Obtener el ID del usuario asociado a la tarjeta
                            query_usuario = "SELECT id_usuario FROM Tarjetas WHERE numero_tarjeta = %s"
                            cursor.execute(query_usuario, (codigo_tarjeta,))
                            usuario = cursor.fetchone()

                            # Insertar los datos en la tabla Sistema_Seguridad
                            if usuario:
                                id_usuario = usuario[0]
                                query_insert = "INSERT INTO Sistema_Seguridad (Id_Tarjeta, Id_Usuario,Descripcion) VALUES (%s,%s, %s)"
                                cursor.execute(query_insert, (id_tarjeta, id_usuario, 'Acceso Concedido'))
                                connection.commit()
                                print("Datos de seguridad insertados correctamente.")
                            else:
                                print("No se encontró el usuario en la base de datos.")
                        else:
                            print("No se encontró la tarjeta en la base de datos.")

                # Retardo de 1000 milisegundos (equivalente a 1 segundo)
                time.sleep(1)

except serial.SerialException as e:
    print("Error al abrir el puerto serial:", e)

except mysql.connector.Error as err:
    print("Error al conectar a la base de datos:", err)

except KeyboardInterrupt:
    print("Proceso interrumpido por el usuario")

finally:
    if 'connection' in locals() and 'cursor' in locals():
        try:
            if connection.is_connected():
                
                cursor.close()
                connection.close()
                print("Conexión a la base de datos cerrada")
        except Exception as e:
            print("Error al cerrar la conexión a la base de datos:",e)
