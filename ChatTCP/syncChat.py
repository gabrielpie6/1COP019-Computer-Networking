import socket             


def chatting(sock, nickname, friend):
    while True:
        message = input(f"[{nickname}]: ")
        if message == "\leave":
            break
        sock.send(message.encode())

        print(f">> Esperando por mensagem...")
        data = sock.recv(4096)
        if not data:
            break
        print(f"[{friend}]: {data.decode()}")
        
        


port = 5001
s = socket.socket()

nickname = input("Entre com nome de usuário: ")
friend = ""

action = input(" [1] Conectar a um usuário\n [2] Esperar por conexão\n>> ")

if action == "1":
    host = input("Endereço IPv4 do usuário: ")
    s.connect((host, port))

    s.send(nickname.encode())
    friend = s.recv(4096).decode()

    print(f"Conectado a {friend}")

    chatting(s, nickname, friend)
    s.close()
else:
    if action == "2":
        host = "127.0.0.1"

        s.bind(('', port))
        s.listen(5)

        print("Esperando por conexão...")
        while True:
            c, addr = s.accept()
            print ('Conectado com ', addr)

            # Envio do nickname escolhido
            c.send(nickname.encode())
            friend = c.recv(4096).decode()

            print(f"Conectado a {friend}")


            # Interação inicial
            print(f">> Esperando por mensagem...")
            data = c.recv(4096)
            if not data:
                break
            print(f"[{friend}]: {data.decode()}")

            # Quebra de conexao apos fim do chat 
            chatting(c, nickname, friend)
            c.close()

            # Finalizacao do programa com quebra de conexao
            break
print(">> Chat finalizado")