
from session import SessionManager

session = SessionManager()

peer = "anfel@example.com"

print("Initial state:", session.get_state())
print("Can chat before connection:", session.is_connected_with(peer))

session.start_call(peer, "test-call-123")
session.confirm_connection()

print("Current state:", session.get_state())
print("Can chat with Anfel:", session.is_connected_with(peer))
print("Can chat with another user:",
      session.is_connected_with("other@example.com"))

session.end_call()

print("After ending call:", session.get_state())
print("Can chat after ending:", session.is_connected_with(peer))
