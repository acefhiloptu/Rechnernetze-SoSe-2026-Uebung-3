import socket
import sys
import threading

clients = {}

def sendHelp(c_sock):
    c_sock.sendall("\n"
        "=== Commands ===\n"
        "help              -> zeigt diese Hilfe\n"
        "clientlist        -> zeigt alle verbundenen Clients\n"
        "send <name> <msg> -> private Nachricht\n"
        "sendall <msg>     -> Nachricht an alle\n"
        "=================\n".encode()
    )

def sendClientList(c_sock):
    msg = f"\nVerbundene Clients: {len(clients)}\n"
    for name in clients:
        msg += f"{name}\n"
    msg += "\n"
    c_sock.sendall(msg.encode())

def broadcast(message, exclude=None):
    for name in clients:
        if name != exclude:
            clients[name].sendall((message + '\n').encode())

def serveClient(c_sock, c_address):
    with c_sock:
        c_sock.sendall("\nBitte registrieren mit:\nregister <name>\n\n".encode())
        line = c_sock.recv(4096).decode().rstrip()
        parts = line.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "register":
            return
        name = parts[1]
        clients[name] = c_sock
        sendHelp(c_sock)
        sendClientList(c_sock)
        broadcast(f"{name} hat den Server betreten", exclude=name)
        while True:
            try:
                line = c_sock.recv(4096).decode().rstrip()
                if not line:
                    break
                parts = line.split(" ", 2)
                if parts[0].lower() == "help":
                    sendHelp(c_sock)
                elif parts[0].lower() == "clientlist":
                    sendClientList(c_sock)
                elif parts[0].lower() == "send":
                    if len(parts) < 3:
                        continue
                    target = parts[1]
                    message = parts[2]
                    if target in clients:
                        clients[target].sendall(
                            f"{name}: {message}\n".encode()
                        )
                        c_sock.sendall(
                            f"{name}: {message}\n".encode()
                        )
                elif parts[0].lower() == "sendall":
                    if len(parts) < 2:
                        continue
                    message = line[len("sendall "):]
                    c_sock.sendall(
                        f"{name} (du an Alle): {message}\n".encode()
                    )
                    broadcast(
                        f"{name} (an Alle): {message}",
                        exclude=name
                    )
            except:
                break
        broadcast(f"{name} hat die Verbindung unterbrochen", exclude=name)
        del clients[name]

def server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_sock:
        s_sock.bind(('0.0.0.0', port))
        s_sock.listen()
        while True:
            c_sock, c_address = s_sock.accept()
            t = threading.Thread(target=serveClient, args=(c_sock, c_address))
            t.start()

def main():
    if len(sys.argv) != 2:
        name = sys.argv[0]
        print(f'Usage: "{name} <port>"')
        sys.exit()
    server(int(sys.argv[1]))

if __name__ == '__main__':
    main()