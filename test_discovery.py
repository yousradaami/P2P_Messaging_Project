
import sys
import time

from discovery import PeerDiscovery


def peer_event(event, peer):

    if event == "online":
        print("\n[ONLINE]", peer["email"])
        print("IP:", peer["ip"])
        print("Chat Port:", peer["chat_port"])

    elif event == "offline":
        print("\n[OFFLINE]", peer["email"])


if len(sys.argv) < 2:

    email = input("Enter your email: ").strip()

else:

    email = sys.argv[1].strip()


if not email:

    print("Email is required.")
    sys.exit(1)


discovery = PeerDiscovery(
    email=email,
    callback=peer_event
)

try:

    discovery.start()

    print("\nWaiting for other peers...")
    print("Press CTRL + C to stop.\n")

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("\nStopping discovery...")

finally:

    discovery.stop()
