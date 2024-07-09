import socket
import threading

class BootstrapServer:
    def __init__(self, host='0.0.0.0', port=6000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((host, port))
        self.nodes = []

    def start(self):
        print("Bootstrap server started")
        threading.Thread(target=self.listen).start()

    def listen(self):
        while True:
            data, addr = self.server.recvfrom(1024)
            message = data.decode()
            if message == 'REGISTER':
                self.nodes.append(addr)
                self.server.sendto("REGISTERED".encode(), addr)
                for node in self.nodes:
                    if node != addr:
                        self.server.sendto(f"{node[0]}:{node[1]}".encode(), addr)
                        self.server.sendto(f"{addr[0]}:{addr[1]}".encode(), node)
            print(f"Nodes: {self.nodes}")

if __name__ == "__main__":
    server = BootstrapServer()
    server.start()
