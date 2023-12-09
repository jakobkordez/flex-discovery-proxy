######################################################
#   FlexRadio discovery Proxy CLIENT
######################################################
#
#   This script connects to the FlexRadio discovery
#   proxy and re-broadcasts all received packets.
#
#   Author:     Jakob Kordež, S52KJ
#
######################################################

from socket import (
    socket,
    AF_INET,
    SOCK_STREAM,
    SOCK_DGRAM,
    IPPROTO_UDP,
    SOL_SOCKET,
    SO_BROADCAST,
)
from select import select
import sys

SERVER = "localhost"
PORT = 4996

broadcastSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
broadcastSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

with socket(AF_INET, SOCK_STREAM) as s:
    s.settimeout(5)
    print("Connecting to server...")

    # Try to connect to the server for 5 seconds
    try:
        s.connect((SERVER, PORT))
        print("Connected to server")
        print("\nPress Ctrl+C to exit...")
    except (ConnectionRefusedError, TimeoutError):
        print("Connection timed out")
        input("\nPress enter to exit...")
        sys.exit(1)

    s.setblocking(False)

    try:
        while True:
            r = select([s], [], [], 1)[0]
            if len(r) == 0:
                continue

            payload = s.recv(2048)
            if not payload:
                print("Server disconnected")
                break

            broadcastSocket.sendto(payload, ("255.255.255.255", 4992))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
