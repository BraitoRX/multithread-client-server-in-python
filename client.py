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
DISCONNECT_MSG = "!END"
hash_incorrecto=0

def receive_messages(client_socket,filename,filesize,id_cliente,num_clients):
    print(f"[CLIENT] Waiting for messages...")
    listo= input("Ingrese READY cuando este listo para recibir el archivo: ")
    client_socket.sendall("READY".encode(FORMAT))
    print(f"[CLIENT] ENVIO DE READY")
    print (f"[CLIENT] Esperando archivo {filename}")
    # verify that dir exists
    if not os.path.exists('ArchivosRecibidos'):
        os.makedirs('ArchivosRecibidos')

    with open(f"ArchivosRecibidos/Cliente{id_cliente}-Prueba-{num_clients}.txt", 'wb') as f:
        offset = 0
        while offset < int(filesize):
            # Leer el archivo en bloques de 1024 bytes
            data = client_socket.recv(SIZE)
            # Enviar el bloque al cliente
            f.write(data)
            offset += len(data)

    client_socket.sendall("FIN".encode(FORMAT))
            
    
    print(f"[CLIENT] Archivo recibido")

    archivo = open(f"ArchivosRecibidos/Cliente{id_cliente}-Prueba-{num_clients}.txt", 'r')
    HASH = client_socket.recv(SIZE).decode(FORMAT)
    HASH_CALCULADO = hashlib.md5(archivo.read().encode()).hexdigest()

    print(f"[CLIENT] HASH recibido: {HASH}")
    print (f"[CLIENT] HASH calculado: {HASH_CALCULADO}")
    correcto_=""
    if HASH == HASH_CALCULADO:
        print(f"[CLIENT] HASH correcto")
        correcto_="correcto"
    else:
        print(f"[CLIENT] HASH incorrecto")
        global hash_incorrecto
        hash_incorrecto+=1
        correcto_="incorrecto"
    client_socket.sendall(correcto_.encode(FORMAT))

    client_socket.close()

def main():
    # Conexión al servidor
    client_sockets = []
    num_clients = int(input("Ingrese el número de clientes: "))
    client_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket_.connect(ADDR)
    print(f"[KING CLIENT] Connected to server at {IP}:{PORT}")
    client_socket_.sendall(str(num_clients).encode(FORMAT))
    archivo_transmision = input("Ingrese el nombre del archivo a transmitir: ")
    print(f"[KING CLIENT] se espera el archivo {archivo_transmision}")
    archivo_transmision = archivo_transmision.encode(FORMAT)
    client_socket_.sendall(archivo_transmision)
    print(f"[KING CLIENT] se envio el nombre del archivo {archivo_transmision}")
    filesize = client_socket_.recv(SIZE).decode(FORMAT)
    print(f"[KING CLIENT] se recibio el tamaño del archivo {filesize}")

    for i in range(num_clients):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(ADDR)
        client_sockets.append(client_socket)
        print(f"[CLIENT {i}] Connected to server at {IP}:{PORT}")

    # Recepción de mensajes
    threads = []
    for i in range(num_clients):
        id_cliente = i
        thread = threading.Thread(target=receive_messages, args=(client_sockets[i],archivo_transmision.decode(FORMAT),filesize,id_cliente,num_clients))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    client_socket_.sendall(DISCONNECT_MSG.encode(FORMAT))
    client_socket_.close()
if __name__ == "__main__":
    main()
    print(f"[CLIENT] HASH incorrectos: {hash_incorrecto}")
