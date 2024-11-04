#!/usr/bin/python3

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

# CONSTANTS
# Set the default proxy server address and port
SERVER = "192.168.1.100"
PORT = 4996


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
import threading
from time import time


class ConnectionThread(threading.Thread):
    def __init__(self, server, port):
        super(ConnectionThread, self).__init__()
        self._stop_event = threading.Event()
        self.server = server
        self.port = port

    def stop(self):
        self._stop_event.set()
        self.join()

    def isStopped(self):
        return self._stop_event.is_set()

    def run(self):
        target = (self.server, self.port)

        # Create broadcast socket
        with socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) as broadcastSocket:
            broadcastSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            # Connect to TCP server
            with socket(AF_INET, SOCK_STREAM) as s:
                print("Connecting to server...", target)

                # Try to connect to the server for 5 seconds
                s.settimeout(5)
                try:
                    s.connect(target)
                    print("Connected to server")
                except (ConnectionRefusedError, TimeoutError):
                    print("Connection timed out")
                    return

                s.setblocking(False)

                while not self._stop_event.is_set():
                    r = select([s], [], [], 1)[0]
                    if len(r) == 0:
                        continue

                    payload = s.recv(2048)
                    if not payload:
                        print("Server disconnected")
                        break

                    # Re-broadcast discovery packet to local network
                    print(f"\r{time()} Received discovery", end="")
                    broadcastSocket.sendto(payload, ("255.255.255.255", 4992))


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    import re

    # Argument parsing
    parser = ArgumentParser(
        prog="client.py",
        description="Connect to a FlexRadio discovery proxy and re-broadcast all received packets",
        epilog="Author: Jakob Kordež, S52KJ",
    )
    parser.add_argument(
        "server",
        metavar="SERVER",
        type=str,
        nargs="?",
        default=SERVER,
        help="Proxy server address (default: %(default)s)",
    )

    args = parser.parse_args()
    sp = re.fullmatch(r"^(?P<host>[^:]+)(:(?P<port>\d+))?$", args.server)
    if not sp:
        print("Invalid server address")
        sys.exit(1)

    SERVER = sp.group("host")
    if sp.group("port"):
        PORT = int(sp.group("port"))

    # Start the connection thread
    thread = ConnectionThread(SERVER, PORT)
    thread.start()
    try:
        while True:
            thread.join(1)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt")
        thread.stop()
    print("Exiting...")
    sys.exit(0)
