
from enum import Enum
import threading


class SessionState(Enum):
    IDLE = "IDLE"
    CALLING = "CALLING"
    RINGING = "RINGING"
    CONNECTED = "CONNECTED"
    BUSY = "BUSY"
    ENDED = "ENDED"


class SessionManager:

    def __init__(self):
        self.state = SessionState.IDLE
        self.current_peer = None
        self.call_id = None
        self.lock = threading.Lock()

    def start_call(self, peer_email, call_id):
        with self.lock:
            if self.state != SessionState.IDLE:
                print("Cannot start call: User is busy!")
                return False

            self.state = SessionState.CALLING
            self.current_peer = peer_email
            self.call_id = call_id

            print(f"Calling {peer_email}...")
            return True

    def receive_call(self, peer_email, call_id):
        with self.lock:
            if self.state != SessionState.IDLE:
                print("Incoming call rejected: BUSY")
                return False

            self.state = SessionState.RINGING
            self.current_peer = peer_email
            self.call_id = call_id

            print(f"Incoming call from {peer_email}")
            return True

    def accept_call(self):
        with self.lock:
            if self.state != SessionState.RINGING:
                return False

            self.state = SessionState.CONNECTED
            print("Call accepted. CONNECTED")
            return True

    def reject_call(self):
        with self.lock:
            if self.state != SessionState.RINGING:
                return False

            self._reset()
            print("Call rejected.")
            return True

    def confirm_connection(self):
        with self.lock:
            if self.state != SessionState.CALLING:
                return False

            self.state = SessionState.CONNECTED
            print("Connection established!")
            return True

    def end_call(self):
        with self.lock:
            if self.state not in (
                SessionState.CALLING,
                SessionState.RINGING,
                SessionState.CONNECTED
            ):
                return False

            print("Call ended.")
            self._reset()
            return True

    def _reset(self):
        self.state = SessionState.IDLE
        self.current_peer = None
        self.call_id = None

    def get_state(self):
        with self.lock:
            return self.state.value

    def is_busy(self):
        with self.lock:
            return self.state in (
                SessionState.CALLING,
                SessionState.RINGING,
                SessionState.CONNECTED
            )

    def is_connected_with(self, peer_email):
        with self.lock:
            if self.state != SessionState.CONNECTED:
                return False

            if not self.current_peer:
                return False

            current = self._clean_email(self.current_peer)
            target = self._clean_email(peer_email)

            return current == target

    @staticmethod
    def _clean_email(email):
        email = str(email).strip().lower()

        if email.startswith("<sip:") and email.endswith(">"):
            email = email[5:-1]
        elif email.startswith("sip:"):
            email = email[4:]

        return email
