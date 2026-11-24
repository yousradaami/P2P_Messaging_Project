
from chat import P2PChat
from session import SessionManager

import sys
import uuid


if len(sys.argv) != 5:
    print(
        "Usage: python chat_network_test.py "
        "EMAIL LOCAL_PORT REMOTE_IP REMOTE_PORT"
    )
    sys.exit(1)


email = sys.argv[1]
local_port = int(sys.argv[2])
remote_ip = sys.argv[3]
remote_port = int(sys.argv[4])

# Create a test session
session = SessionManager()

peer_email = input("Enter peer email: ").strip()

# Simulate an established SIP session for this test
call_id = str(uuid.uuid4())

session.start_call(peer_email, call_id)
session.confirm_connection()

# Create RTP chat
chat = P2PChat(
    local_port=local_port,
    remote_ip=remote_ip,
    remote_port=remote_port,
    session_manager=session,
    peer_email=peer_email
)

chat.start()

print(f"\nLogged in as: {email}")
print(f"Connected with: {peer_email}")
print("Type a message. Type /exit to stop.\n")

try:
    while True:
        message = input()

        if message == "/exit":
            break

        if message.strip():
            chat.send_message(message)

finally:
    chat.stop()
    session.end_call()
