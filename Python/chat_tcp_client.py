import socket
import sys
import threading

def receiveLines(c_sock):
    while True:
        try:
            line = c_sock.recv(4096).decode().rstrip()
            if not line:
                break
            print(line)
            if line.lower() == 'stop':
                break
        except:
            break

def sendLines(c_sock):
    while True:
        line = input().rstrip()
        c_sock.sendall((line + '\n').encode())
        if line.lower() == 'stop':
            break

def client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c_sock:
        c_sock.connect((host, port))
        t = threading.Thread(target=receiveLines, args=(c_sock,))
        t.daemon = True
        t.start()
        sendLines(c_sock)

def main():
    if len(sys.argv) != 3:
        name = sys.argv[0]
        print(f'Usage: "{name} <ip> <port>"')
        sys.exit()
    client(sys.argv[1], int(sys.argv[2]))

if __name__ == '__main__':
    main()