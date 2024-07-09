import argparse
import threading
from p2pnetwork.node import Node
import stun
import socket

class PeerNode(Node):
    def __init__(self, host, port):
        super(PeerNode, self).__init__(host, port, None)
        self.peers = []

    def inbound_node_connected(self, node):
        print(f"Inbound connection from {node.host}:{node.port}")
        self.peers.append(node)

    def outbound_node_connected(self, node):
        print(f"Outbound connection to {node.host}:{node.port}")
        self.peers.append(node)

    def node_disconnected(self, node):
        print(f"Node disconnected {node.host}:{node.port}")
        self.peers.remove(node)

    def node_message(self, node, data):
        print(f"Message from {node.host}:{node.port}: {data}")

    def send_message(self, message):
        for peer in self.peers:
            self.send_to_node(peer, message)

def start_node(host, port):
    node = PeerNode(host, port)
    node.start()
    return node

def get_public_address():
    nat_type, external_ip, external_port = stun.get_ip_info(stun_host='stun.l.google.com', stun_port=19302)
    print(f"Public IP: {external_ip}, Public Port: {external_port}")
    return external_ip, external_port

def register_with_bootstrap(bootstrap_host, bootstrap_port, public_ip, public_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto("REGISTER".encode(), (bootstrap_host, bootstrap_port))
    client.recvfrom(1024)  # ACK from server
    client.sendto(f"{public_ip}:{public_port}".encode(), (bootstrap_host, bootstrap_port))

    peers = []
    while True:
        data, _ = client.recvfrom(1024)
        peer_info = data.decode().split(':')
        peers.append((peer_info[0], int(peer_info[1])))
        if len(peers) > 1:
            break
    return peers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='P2P Network Node')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='Host address to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument('--bootstrap_host', type=str, required=True, help='Bootstrap server host')
    parser.add_argument('--bootstrap_port', type=int, required=True, help='Bootstrap server port')

    args = parser.parse_args()

    public_ip, public_port = get_public_address()
    print(f"Starting local node with public address {public_ip}:{public_port}")

    # Register with the bootstrap server
    peers = register_with_bootstrap(args.bootstrap_host, args.bootstrap_port, public_ip, public_port)
    print(f"Peers found: {peers}")

    # Start the local peer node
    local_node = start_node(args.host, args.port)

    # Connect to peers
    for peer in peers:
        local_node.connect_with_node(peer[0], peer[1])

    while True:
        command = input("Enter command (send/exit): ")
        if command == "send":
            message = input("Enter message: ")
            local_node.send_message(message)
        elif command == "exit":
            local_node.stop()
            break
