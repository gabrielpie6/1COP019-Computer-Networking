import dearpygui.dearpygui as dpg

import socket
import threading
import queue


listen_thread = threading.Thread(target=None, args=(0,))
send_thread   = threading.Thread(target=None, args=(0,))
shared_queue  = queue.Queue()

def do_Connection(sender, app_data, user_data):
    global listen_thread
    global send_thread
    
    host     = dpg.get_value("input_host")
    nickname = dpg.get_value("input_nickname")

    show_second_window(sender, app_data, user_data)

    listen_thread = threading.Thread(target=listen_on_port, args=(5001,))
    send_thread   = threading.Thread(target=send_to_port,   args=(host, 5001, nickname))

    listen_thread.start()
    send_thread.start()
    

    
    




def listen_on_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', port))
        server_socket.listen(5)
        print(f"Esperando por conexões na porta {port}...")
        
        conn, addr = server_socket.accept()
        with conn:
            friend = conn.recv(4096).decode()
            print(f"Conectado com [{friend}] por {addr}")
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                dpg.set_value("output_text", f'{dpg.get_value("output_text")}\n[{friend}]: {data.decode()}')

def send_to_port(host, port, nickname):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            client_socket.connect((host, port))
            break
        except ConnectionRefusedError:
            continue

    client_socket.sendall(nickname.encode())

    closed = False
    while not closed:
        if not shared_queue.empty():
            message = shared_queue.get()
            if message == "\leave":
                closed = True
                break
            try:
                client_socket.sendall(message.encode())
            except Exception as e:
                closed = True
    client_socket.close()







def show_second_window(sender, app_data, user_data):
    dpg.set_viewport_height(435)

    # Obtendo os valores dos inputs
    host = dpg.get_value("input_host")
    mode = dpg.get_value("input_mode")
    nickname = dpg.get_value("input_nickname")

    # Fechando a primeira janela
    dpg.delete_item("primeira_janela")


    def on_enter_pressed(sender, app_data, user_data):
        input_text = dpg.get_value("input_text")
        dpg.set_value("output_text", f'{dpg.get_value("output_text")}\n[{nickname}]: {input_text}')
        shared_queue.put(input_text)
        dpg.set_y_scroll("scrolling_region", dpg.get_y_scroll_max("scrolling_region") + 13.0)
        dpg.focus_item("input_text")

    def close_connection(sender, app_data, user_data):
        shared_queue.put("\leave")
        dpg.stop_dearpygui()

    with dpg.window(width=300, height=400, tag="mainContainer", label="Janela de Conversa"):
        with dpg.group(horizontal=False):
            with dpg.child_window(tag="scrolling_region", width=-1, height=335, border=False):
                dpg.add_text("", tag="output_text")
                dpg.set_y_scroll("scrolling_region", dpg.get_y_scroll_max("scrolling_region"))
        with dpg.group(horizontal=True):
            dpg.add_input_text(label="", tag="input_text", default_value="mensagem", on_enter=True, callback=on_enter_pressed, user_data=True, width=230)
            dpg.add_button(label="Sair", callback=close_connection)

dpg.create_context()

# Criando a primeira janela
with dpg.window(label="Janela de Conexao", width=300, height=220, tag="primeira_janela"):
    dpg.add_input_text(default_value="", label="Host IPv4", tag="input_host")
    dpg.add_input_text(label="Nickname", tag="input_nickname")
    dpg.add_button(label="Confirmar", callback=do_Connection)



dpg.create_viewport(title='ChatTCP Assincrono', width=300, height=220)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

listen_thread.join()
send_thread.join()