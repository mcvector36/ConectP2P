import argparse
import threading
from p2pnetwork.node import Node
import stun

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='P2P Network Node')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='Host address to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')

    args = parser.parse_args()

    public_ip, public_port = get_public_address()
    print(f"Starting local node with public address {public_ip}:{public_port}")

    # Start the local peer node
    local_node = start_node(args.host, args.port)

    while True:
        command = input("Enter command (exit to quit): ")
        if command == "exit":
            local_node.stop()
            break
