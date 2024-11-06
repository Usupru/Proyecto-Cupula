# Importamos modulos necesarios
import time
from flask import Flask, render_template, request
import bluetooth

# Definimos las variables globales necesarias
sock = None
hc05_address = None

# Creamos una instancia Flask
app = Flask(__name__)

# Funcion para buscar el modulo bluetooth HC-05

def find_hc05():
    global hc05_address
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True) # Busca dispositivos BT
    for addr, name in nearby_devices: # Hacemos un for loop por todos los dispositivos encontrados
        if "HC-05" in name: # Si encontramos un HC-05 cambia el valor de la variable a la direccion MAC del modulo
            hc05_address = addr
            print(f"HC-05 found at address {hc05_address}")
            return addr
    print("HC-05 not found")
    return None

# Funcion para conectarse al HC-05 una vez encontrada la MAC

def connect_hc05():
    port = 1  # Puerto predeterminado para SPP
    global sock
    global hc05_address
    if hc05_address is None:
        print("No HC-05 address available.")
        return None

    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM) # Creamos una instancia sock
    try: # Intentamos conectar al HC-05 mediante la instancia sock
        print(f"Attempting to connect to HC-05 at {hc05_address}...")
        sock.connect((hc05_address, port))
        print("Connection to HC-05 successful")
        return sock
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Failed to connect: {e}")
        return None

# Funcion para mover la cupula a la izquierda

def left(sock):
    command = 'L'
    sock.send(command)
    response = sock.recv(1024).decode('utf-8')
    return response

# Funcion para mover la cupula a la derecha

def right(sock):
    command = 'R'
    sock.send(command)
    response = sock.recv(1024).decode('utf-8')
    return response

# Funcion main que se ejecuta al principio del programa

def main():

    global sock

    print("Searching HC-05")
    find_hc05()

    if hc05_address:
        print("Connecting to HC-05")
        sock = connect_hc05()
    
        if sock is None:
            print("Error: Connection with HC-05 failed")
        else:
            print("Connection successful")
    else:
        print("No HC-05 device found. Retrying in 5 seconds...")
        time.sleep(5)  # Espera antes de intentar nuevamente
        main()  # Intentar encontrar de nuevo


# Listener de las interacciones del usuario en la web

@app.route('/', methods=['GET', 'POST'])
def index():
    global sock
    response = None
    if request.method == 'POST': # En caso de obtener una request con el header POST, proseguir
        action = request.form.get('action') # Obtenemos la respuesta del usuario respecto a los dos botones
        if sock:
            try:
                if action == 'left': # Si la accion es left, se ejecute la funcion left()
                    response = left(sock)
                elif action == 'right': # Si la accion es right, se ejecute la funcion right()
                    response = right(sock)
                else:
                    response = "Error"
            except Exception as e:
                response = f"Error durante la comunicación: {e}"
        
        else:
            response = "HC-05 not found" # Si no hay un sock, el HC-05 no esta conectado

    return render_template('index.html', response=response) # Renderizamos la respuesta

# Ejecuta el programa

if __name__ == '__main__':
    main()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=80) # Una vez que la funcion main se termina de ejecutar nos ponemos a escuchar en el puerto 80
                                                                                                                                                                                                    