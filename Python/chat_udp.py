import socket
import sys
import threading

def receiveLines(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_sock:
        s_sock.bind(('0.0.0.0', port))
        while True:
            line, c_address = s_sock.recvfrom(4096)
            line = line.decode().rstrip()
            if line.lower() == "nachricht empfangen!":
                print("Nachricht empfangen")
                continue
            parts = line.split(" ", 3)
            if len(parts) >= 4 and parts[0].lower() == "send":
                target_ip = parts[1]
                target_port = int(parts[2])
                message = parts[3]
                print(f'<{c_address[0]}:{c_address[1]}> -> '
                      f'<{target_ip}:{target_port}>, "{message}"')
                s_sock.sendto(message.encode(), (target_ip, target_port))
            else:
                print(f'Message <{repr(line)}> received from client {c_address}')
            s_sock.sendto("Nachricht empfangen!".encode(), c_address)
            if line.lower() == 'stop':
                break

def sendLines(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as c_sock:
        while True:
            line = input().rstrip()
            parts = line.split(" ", 3)
            if len(parts) < 4 or parts[0].lower() != "send":
                print("Usage: send <ip> <port> <message>")
                continue
            c_sock.sendto(line.encode(), (host, port))
            ack, _ = c_sock.recvfrom(4096)
            print(ack.decode().rstrip())
            if parts[3].lower() == 'stop':
                break

def main():
    if len(sys.argv) == 3 and sys.argv[1].lower() == '-l':
        port = int(sys.argv[2])
        receiveLines(port)

    elif len(sys.argv) == 4:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        local_port = int(sys.argv[3])

        t = threading.Thread(target=receiveLines, args=(local_port,))
        t.daemon = True
        t.start()

        sendLines(server_ip, server_port)

    else:
        name = sys.argv[0]
        print(f'Usage: "{name} -l <port>" or '
              f'"{name} <server_ip> <server_port> <local_port>"')
        sys.exit()

if __name__ == '__main__':
    main()