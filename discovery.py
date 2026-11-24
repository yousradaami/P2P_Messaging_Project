
import socket
import json
import uuid
import time
import threading

from config import (
    MULTICAST_GROUP,
    MULTICAST_PORT,
    ANNOUNCE_INTERVAL,
    PEER_TIMEOUT,
    MULTICAST_TTL,
    CHAT_PORT
)


class PeerDiscovery:

    def __init__(self, email, callback=None):
        self.email = email
        self.peer_id = str(uuid.uuid4())
        self.callback = callback
        self.peers = {}

        self.running = False
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self.receiver_socket = None
        self.sender_socket = None

    def start(self):

        if self.running:
            return

        self.stop_event.clear()

        try:
            self.receiver_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM,
                socket.IPPROTO_UDP
            )

            self.receiver_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            self.receiver_socket.bind(("", MULTICAST_PORT))

            membership = (
                socket.inet_aton(MULTICAST_GROUP)
                + socket.inet_aton("0.0.0.0")
            )

            self.receiver_socket.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                membership
            )

            self.receiver_socket.settimeout(0.5)

            self.sender_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM,
                socket.IPPROTO_UDP
            )

            self.sender_socket.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_MULTICAST_TTL,
                MULTICAST_TTL
            )

            self.sender_socket.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_MULTICAST_LOOP,
                1
            )

            self.running = True

            threading.Thread(
                target=self.receive_loop,
                daemon=True
            ).start()

            threading.Thread(
                target=self.announce_loop,
                daemon=True
            ).start()

            print("UDP Multicast Discovery started!")
            print("Email:", self.email)
            print("Peer ID:", self.peer_id)

        except OSError as error:
            self.stop()
            raise RuntimeError(
                f"Could not start discovery: {error}"
            )

    def announce_loop(self):

        while not self.stop_event.is_set():

            message = {
                "type": "DISCOVER",
                "peer_id": self.peer_id,
                "email": self.email,
                "chat_port": CHAT_PORT
            }

            try:
                data = json.dumps(message).encode("utf-8")

                self.sender_socket.sendto(
                    data,
                    (MULTICAST_GROUP, MULTICAST_PORT)
                )

            except OSError as error:
                if not self.stop_event.is_set():
                    print("Announcement error:", error)

            self.stop_event.wait(ANNOUNCE_INTERVAL)

    def receive_loop(self):

        while not self.stop_event.is_set():

            try:
                data, address = self.receiver_socket.recvfrom(4096)

                message = json.loads(data.decode("utf-8"))

                if message.get("type") != "DISCOVER":
                    continue

                received_id = message.get("peer_id")
                received_email = message.get("email")
                received_port = message.get("chat_port")

                if received_id == self.peer_id:
                    continue

                if not isinstance(received_id, str) or not received_id:
                    continue

                if not isinstance(received_email, str) or not received_email:
                    continue

                if type(received_port) is not int:
                    continue

                if not (1 <= received_port <= 65535):
                    continue

                peer = {
                    "peer_id": received_id,
                    "email": received_email,
                    "ip": address[0],
                    "chat_port": received_port,
                    "last_seen": time.monotonic()
                }

                with self.lock:
                    is_new = received_id not in self.peers
                    self.peers[received_id] = peer

                if is_new:
                    print(
                        f"New peer discovered: "
                        f"{received_email} ({address[0]})"
                    )

                    if self.callback:
                        self.callback("online", peer)

            except socket.timeout:
                pass

            except (OSError, ValueError, UnicodeDecodeError) as error:
                if not self.stop_event.is_set():
                    print("Receive error:", error)

            self.remove_inactive_peers()

    def remove_inactive_peers(self):

        current_time = time.monotonic()

        with self.lock:
            inactive_ids = [
                peer_id
                for peer_id, peer in self.peers.items()
                if current_time - peer["last_seen"] > PEER_TIMEOUT
            ]

            removed_peers = [
                self.peers.pop(peer_id)
                for peer_id in inactive_ids
            ]

        for peer in removed_peers:
            print(f"Peer disconnected: {peer['email']}")

            if self.callback:
                self.callback("offline", peer)

    def get_peers(self):

        with self.lock:
            return [
                peer.copy()
                for peer in self.peers.values()
            ]

    def stop(self):

        self.running = False
        self.stop_event.set()

        for sock in (
            self.receiver_socket,
            self.sender_socket
        ):

            if sock:
                try:
                    sock.close()
                except OSError:
                    pass

        self.receiver_socket = None
        self.sender_socket = None

        print("UDP Multicast Discovery stopped.")
