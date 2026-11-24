
import socket
import threading

from rtp import RTPPacket, parse_packet


class P2PChat:

    def __init__(
        self,
        local_port,
        remote_ip,
        remote_port,
        session_manager,
        peer_email,
        on_message=None
    ):
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port

        self.session_manager = session_manager
        self.peer_email = peer_email
        self.on_message = on_message

        self.socket = None
        self.running = False
        self.rtp_sender = RTPPacket()

    def start(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.socket.bind(("0.0.0.0", self.local_port))
        self.socket.settimeout(1)

        self.running = True

        receiver = threading.Thread(
            target=self._receive_messages,
            daemon=True
        )

        receiver.start()

        print(f"RTP Chat started on port {self.local_port}")

    def send_message(self, message):

        if not self.session_manager.is_connected_with(self.peer_email):
            print("Cannot send: No active session with this peer!")
            return False

        if not self.running:
            print("Chat is not running!")
            return False

        packet = self.rtp_sender.create_packet(message)

        self.socket.sendto(
            packet,
            (self.remote_ip, self.remote_port)
        )

        print(f"You: {message}")
        return True

    def _receive_messages(self):

        while self.running:
            try:
                data, address = self.socket.recvfrom(65535)

                if not self.session_manager.is_connected_with(
                    self.peer_email
                ):
                    print("Message ignored: No active session.")
                    continue

                received = parse_packet(data)
                message = received["message"]

                print(f"\nPeer: {message}")

                if self.on_message:
                    self.on_message(message)

            except socket.timeout:
                continue

            except ValueError as error:
                print(f"Invalid RTP packet: {error}")

            except OSError:
                break

    def stop(self):
        self.running = False

        if self.socket:
            self.socket.close()
            self.socket = None

        print("RTP Chat stopped.")
