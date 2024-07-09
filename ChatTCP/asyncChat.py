import socket
import threading

#
# Função de escuta de mensagens controlada por Thread
def listen_on_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', port))
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


#
# Funcao de envio de mensagens controlada por Thread
def send_to_port(host, port):
    global nickname
    global friend
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Tenta se conectar ao host na porta especificada
    while True:
        try:
            client_socket.connect((host, port))
            break
        except ConnectionRefusedError:
            continue


    client_socket.sendall(nickname.encode())

    # Enquanto a conexão não for fechada pelo usuário, envia mensagens vindas da entrada de teclado
    while True:
        message = input(f"[{nickname}]: ")
        if message == "\leave":
            break
        client_socket.sendall(message.encode())
    client_socket.close()






nickname = input("Entre com nome de usuário: ")
host     = input("Endereço IPv4 do usuário: ")
port     = int(input("Porta de conexão: "))




# Criação das threads
listen_thread = threading.Thread(target=listen_on_port, args=(port,))
send_thread   = threading.Thread(target=send_to_port,   args=(host, port))
    


# Início das threads
listen_thread.start()
send_thread.start()

listen_thread.join()
send_thread.join()