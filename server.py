import socket
import threading
import wikipedia
import hashlib
import os

IP = "192.168.20.57"
# IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def handle_client(conn:socket, addr,filename,cantidad_clientes):
    print(f"[NEW CONNECTION] {addr} connected.")
    listo = conn.recv(SIZE).decode(FORMAT)
    print(f"[READY][{addr}] {listo}")
    if listo == "READY":
        ALLready.append(conn)
    while len(ALLready) < cantidad_clientes:
        print(f"[READY][{addr}] Esperando a que todos los clientes esten listos")
        pass

    

    archivo = open(filename, "r")
    tamaño = os.path.getsize(filename)
    print(f"[ARCHIVO][{addr}] {filename} abierto")
    # enviar el archivo por bloques de 1024 bytes

    with open(filename, 'rb') as f:
        offset = 0
        while offset < tamaño:
            # Leer el archivo en bloques de 1024 bytes
            data = f.read(SIZE)
            # Enviar el bloque al cliente
            conn.sendall(data)
            offset += len(data) 

    conn.sendall("FIN".encode(FORMAT))


    print(f"[ARCHIVO][{addr}] {filename} enviado")
    hash_archivo = hashlib.md5(archivo.read().encode()).hexdigest()
    print(f"[ARCHIVO][HASH][{addr}] {filename} leido")
    conn.sendall(hash_archivo.encode(FORMAT))
    print(f"[ARCHIVO][HASH][{addr}] {filename} enviado")
    conn.close()
    
    

def main():
    global ALLready
    
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    conexion_inicial, addr = server.accept()
    print(f"[KING CONNECTION] {addr} connected.")
    cantidad_clientes = int(conexion_inicial.recv(SIZE).decode(FORMAT))
    print(f"[KING CONNECTION] se esperan {cantidad_clientes} clientes")
    archivo_transmision = conexion_inicial.recv(SIZE).decode(FORMAT)+".txt"
    print(f"[KING CONNECTION] espera el archivo {archivo_transmision}")
    conexion_inicial.sendall(str(os.path.getsize(archivo_transmision)).encode(FORMAT))
    ALLready = []

    
    
    for i in range(cantidad_clientes):
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr,archivo_transmision,cantidad_clientes))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    while True:
        command = input("[SERVER] Enter command: ")
        if command == DISCONNECT_MSG:
            break
    
    print("[SERVER] Server is stopping...")
    server.close()
    print("[SERVER] Server stopped.")


if __name__ == "__main__":
    main()
