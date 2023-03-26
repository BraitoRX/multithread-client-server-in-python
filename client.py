import socket
import threading
import os 
import hashlib
IP = "192.168.20.57"
# IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
hash_incorrecto=0

def receive_messages(client_socket,filename):
    print(f"[CLIENT] Waiting for messages...")
    client_socket.sendall("READY".encode(FORMAT))
    print(f"[CLIENT] ENVIO DE READY")
    print (f"[CLIENT] Esperando archivo {filename}")
    # verify that dir exists
    if not os.path.exists('received_files'):
        os.makedirs('received_files')

    with open('received_files/' + filename+".txt", 'wb') as f:
        while True:
            data = client_socket.recv(SIZE)
            if data == b'FIN':
                print(f"[CLIENT] Archivo recibido")
                break
            f.write(data)

    archivo = open('received_files/' + filename+".txt", "r")
    HASH = client_socket.recv(SIZE).decode(FORMAT)
    HASH_CALCULADO = hashlib.md5(archivo.read().encode()).hexdigest()

    print(f"[CLIENT] HASH recibido: {HASH}")
    print (f"[CLIENT] HASH calculado: {HASH_CALCULADO}")

    if HASH == HASH_CALCULADO:
        print(f"[CLIENT] HASH correcto")
    else:
        print(f"[CLIENT] HASH incorrecto")
        global hash_incorrecto
        hash_incorrecto+=1

    

    client_socket.close()

def main():
    # Conexión al servidor
    client_sockets = []
    num_clients = int(input("Ingrese el número de clientes: "))
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)
    print(f"[KING CLIENT] Connected to server at {IP}:{PORT}")
    client_socket.sendall(str(num_clients).encode(FORMAT))
    archivo_transmision = input("Ingrese el nombre del archivo a transmitir: ")
    print(f"[KING CLIENT] se espera el archivo {archivo_transmision}")
    archivo_transmision = archivo_transmision.encode(FORMAT)
    client_socket.sendall(archivo_transmision)

    for i in range(num_clients):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(ADDR)
        client_sockets.append(client_socket)
        print(f"[CLIENT {i}] Connected to server at {IP}:{PORT}")

    # Recepción de mensajes
    threads = []
    for i in range(num_clients):
        thread = threading.Thread(target=receive_messages, args=(client_sockets[i],archivo_transmision.decode(FORMAT)))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
if __name__ == "__main__":
    main()
    print(f"[CLIENT] HASH incorrectos: {hash_incorrecto}")
