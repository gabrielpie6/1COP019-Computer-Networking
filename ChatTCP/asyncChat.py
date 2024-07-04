import socket
import threading

# Função para ouvir mensagens na porta 5001
def listen_on_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', port))
        server_socket.listen(5)
        print(f"Esperando por conexões na porta {port}...")
        
        conn, addr = server_socket.accept()
        with conn:
            friend = conn.recv(1024).decode()
            print(f"Conectado com [{friend}] por {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"[{friend}]: {data.decode()}\n")

# Função para enviar mensagens para a porta 5001
def send_to_port(host, port):
    global nickname
    global friend
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            client_socket.connect((host, port))
            break
        except ConnectionRefusedError:
            # print("Connection refused. Retrying...")
            continue
    # client_socket.connect((host, 5002))

    client_socket.sendall(nickname.encode())

    while True:
        message = input(f"[{nickname}]: ")
        #print(f"[{nickname}]: {message}")
        client_socket.sendall(message.encode())



nickname = input("Entre com nome de usuário: ")
host = input("Endereço IPv4 do usuário: ")

action = input(" [1] Conectar a um usuário\n [2] Esperar por conexão\n>> ")

listen_thread = threading.Thread(target=None, args=(0,))
send_thread   = threading.Thread(target=None, args=(0,))

if action == "1":
    listen_thread = threading.Thread(target=listen_on_port, args=(5001,))
    send_thread   = threading.Thread(target=send_to_port,   args=(host, 5002))
else:
    if action == "2":
        listen_thread = threading.Thread(target=listen_on_port, args=(5002,))
        send_thread   = threading.Thread(target=send_to_port,   args=(host, 5001))
    


# Criação e início das threads
# listen_thread = threading.Thread(target=listen_on_port)
# send_thread = threading.Thread(target=send_to_port, args=(host,))

listen_thread.start()
send_thread.start()

listen_thread.join()
send_thread.join()