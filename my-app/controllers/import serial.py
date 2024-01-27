import serial

# Configurar el puerto serial (debes cambiar el nombre del puerto serial según tu sistema operativo)
puerto_serial = 'COM3'  # Linux
#puerto_serial = 'COM3'  # Windows

# Velocidad de comunicación (baud rate)
baud_rate = 9600

try:
    # Abrir el puerto serial
    with serial.Serial(puerto_serial, baud_rate) as puerto:
        # Leer datos del puerto serial hasta que se reciba una línea vacía
        while True:
            linea = puerto.readline().decode().strip()
            if linea:
                datos=linea.split(":")
                if datos[0]=="temp":
                    #aqui se manda a la tabla de temperatura
                    print("Aqui se esta recibiendo la temperatura")
                    print(datos[1])
                elif datos[0]=="alertaTemp":
                    #hago algo 
                    print("Aqui se esta recibiendo la alerta")
                    print(datos[1])
                else:
                    print(datos)
            else:
                break

except serial.SerialException as e:
    print("Error al abrir el puerto serial:", e)

except KeyboardInterrupt:
    print("Proceso interrumpido por el usuario")

finally:
    if puerto.is_open:
        puerto.close()
        print("Puerto serial cerrado correctamente")
