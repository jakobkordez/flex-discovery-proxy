######################################################
#   FlexRadio discovery Proxy
######################################################
#
#   This script listens for FlexRadio discovery
#   packets on UDP port 4992 and forwards them
#   over a TCP connection to all connected clients.
#
#   Author:     Jakob Kordež, S52KJ
#
######################################################

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from select import select
from time import time
import sys

TCP_PORT = 4996
UDP_PORT = 4992

# Listen for clients
tcp_socket = socket(AF_INET, SOCK_STREAM)
tcp_socket.bind(("", TCP_PORT))
tcp_socket.listen(5)
tcp_socket.setblocking(False)

# Listen for Discovery packets
udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind(("", UDP_PORT))
udp_socket.setblocking(False)

clients: list[socket] = []

print("\nPress Ctrl+C to exit...")

try:
    while True:
        r = select([tcp_socket, udp_socket, *clients], [], [], 1)[0]
        s: socket
        for s in r:
            if s is tcp_socket:
                # A client has connected
                connection, client_address = tcp_socket.accept()
                connection.setblocking(False)
                clients.append(connection)
                print("New connection from:", client_address)
            elif s is udp_socket:
                # Discovery packet received
                data, client_address = udp_socket.recvfrom(2048)
                print(int(time()), "Received discovery")

                # Send discovery packet to all clients
                for c in clients:
                    c.send(data)
            else:
                try:
                    data = s.recv(1024)
                except:
                    data = None
                if not data:
                    # A client socket has been disconnected
                    print("Client disconnected:", s.getpeername())
                    clients.remove(s)
                    s.close()
except KeyboardInterrupt:
    print("\nExiting...")
    for s in clients:
        s.close()
    tcp_socket.close()
    udp_socket.close()
    sys.exit(0)
