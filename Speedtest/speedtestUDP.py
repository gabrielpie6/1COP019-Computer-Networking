import socket
import time
import sys
import threading

from tabulate import tabulate

class Packet:
    msg = "teste de rede *2024*"
    size = 500
    lim = size - 38 - 2
    id = 0
    def __init__(self) -> None:
        self.id   = Packet.id
        self.msg  = (Packet.msg * (Packet.lim // len(Packet.msg) + 1))[:Packet.lim]
        
        Packet.id = Packet.id + 1
    def toData(self):
        return f"{self.id:06d},{self.msg}"





def createSocket(protocol):
    if (protocol == "TCP"):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif (protocol == "UDP"):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        return None























def server(host, port, protocol):
    global END_OF_TRANS

    s = createSocket(protocol)
    sc = createSocket("TCP")

    s.bind((host, port))
    # s.listen(10)

    sc.bind((host, port + 1))
    sc.listen(10)




    while True:
        END_OF_TRANS = False
        # print(f'Esperando por conexão na porta {port}...')
        # connection, addr = s.accept()
        # print(f'Conexão estabelecida com {addr}')
        
        # print(f'Esperando por conexão na porta {port + 1}...')
        control, addr = sc.accept()
        print(f'Conexão estabelecida com {addr}')


        receivedPackages, receivedBytes, elapsedTime = donwload(s, control)
        time.sleep(1)

        print("Teste finalizado")
        sendServerData(control, (receivedPackages, receivedBytes, elapsedTime))

def client(host, port, protocol):
    s  = createSocket(protocol)
    sc = createSocket("TCP")
    

    dest = input("Endereço IPv4 de destino: ")
    while True:
        try:
            # s.connect((dest, port))
            # print("Conexão estabelecida com sucesso!")
            sc.connect((dest, port + 1))
            print("Conexão estabelecida com sucesso!")

            seconds = float(input("Duração do teste (s): "))

            sentPackages, bytesSent = upload(s, sc, seconds, (dest, port))

            print("uploaded")

            result = receiveServerData(sc)
            receivedPackages, receivedBytes, elapsedTime = result
            return sentPackages, bytesSent, int(receivedPackages), int(receivedBytes), float(elapsedTime), seconds
            break

        except Exception as e:
            print("Conexão mal-sucedida. Tentando novamente...")
            time.sleep(1)

        finally:
            s.close()



##########################################
##########################################
#

#
def sendServerData(control:socket.socket, data: tuple):
    msg = ",".join([str(x) for x in data])
    control.sendall(msg.encode("utf-8"))
def receiveServerData(control:socket.socket):
    data = control.recv(1024)
    return data.decode("utf-8").split(",")
#
def listenToEOT(connection: socket.socket):
    global END_OF_TRANS

    listening = True

    while listening:
        data = connection.recv(1024)
        if(data):
            with lock:
                END_OF_TRANS = True
                listening = False
        else:
            break
#
def sendPackets(s: socket.socket, control: socket.socket, seconds:float, addr):
    startTime    = time.time()
    timeElapsed  = 0.0
    sentPackages = 0
    bytesSent    = 0

    while (timeElapsed < seconds):
        encodedData = Packet().toData().encode("utf-8")
        packetSize  = sys.getsizeof(encodedData)
        # s.sendall(encodedData)

        s.sendto(encodedData, addr)

        print(f" - [{sentPackages:06d}] Pacote enviado, size={packetSize} B, total={bytesSent} B")
        
        sentPackages += 1
        bytesSent    += packetSize
        timeElapsed   = time.time() - startTime
    s.sendto("END_PACKET_STREAM".encode("utf-8"), addr)
    control.sendall("END_OF_TRANS".encode("utf-8"))
    s.close()

    return sentPackages, bytesSent
#
def receivePackets(connection: socket.socket, recvResult:list):
    global END_OF_TRANS

    receivedPackages = 0
    receivedBytes    = 0
    startTime        = 0.0
    endTime          = 0.0
    firstPacket      = True

    while True:
        with lock:
            if END_OF_TRANS:
                endTime = time.time()
                print("stopped recieving")
                break
        data, addr = connection.recvfrom(1024)
        if (data):
            receivedPackages += 1
            packetSize        = sys.getsizeof(data)
            receivedBytes    += packetSize
            str               = data.decode("utf-8")

            if (str == "END_PACKET_STREAM"):
                receivedBytes    -= packetSize
                receivedPackages -= 1
                endTime = time.time()
                print("stopped recieving")
                break

            print(f" - [{str[:6]}] Pacote recebido, size={packetSize} B, total={receivedBytes} B")
            if firstPacket:
                firstPacket = False
                startTime = time.time()
        else:
            endTime = time.time()
            break
    print("FIM")
    recvResult.append(receivedPackages)
    recvResult.append(receivedBytes)
    recvResult.append(endTime - startTime)
    
    return receivedPackages, receivedBytes, endTime - startTime
    
#
##########################################
##########################################





def upload(client, control, seconds, addr):
    sentPackages, bytesSent = sendPackets(client, control, seconds, addr)
    return sentPackages, bytesSent

def donwload(server, control):
    recvResult = []
    thread1 = threading.Thread(target=listenToEOT,    args=(control, ))
    thread2 = threading.Thread(target=receivePackets, args=(server,  recvResult))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    return recvResult[0], recvResult[1], recvResult[2]














# CONTROLES
END_OF_TRANS    = False
lock            = threading.Lock()
if __name__ == "__main__":
    host = input("Digite o IP da sua máquina na rede: ")

    action = input(" [1] Esperar por conexão\n [2] Conectar a um usuário\n>> ")
    if   action == "1":
        server(host, 5001, "UDP")

        
        print("FIM server")


    elif action == "2":
        sentPackages, bytesSent, receivedPackages, receivedBytes, elapsedTime, seconds = client(host, 5001, "UDP")

        packetLoss        = sentPackages     - receivedPackages
        packetLossPercent = packetLoss       / sentPackages * 100
        speedData         = receivedBytes    / elapsedTime
        speedPackets      = receivedPackages / elapsedTime
        
        table = [
            ["Pacotes Enviados",                    f"{sentPackages:,}"],
            ["Pacotes Recebidos",                   f"{receivedPackages:,}"],
            ["Pacotes Perdidos",                    f"{packetLoss} ({packetLossPercent:.2f}%)"],
            ["Bytes enviados (B)",                  f"{bytesSent:,}"],
            ["Bytes recebidos (B)",                 f"{receivedBytes:,}"],
            ["Tempo de Envio (s)",                     seconds],
            ["Tempo total de transmissão (s)",      f"{elapsedTime:.4f}"],
            ["Velocidade (B/s)",                    f"{speedData:,.2f}"],
            ["Velocidade (MB/s)",                   f"{speedData/1000000:,.2f}"],
            ["Velocidade (Packets/s)",              f"{speedPackets:,.2f}"]
        ]
        print(tabulate(table, headers=["Parâmetro", "Valor"], tablefmt="pretty"))
        print(f">> Teste finalizado")