
# ==============================
# NETWORK CONFIGURATION
# ==============================

MULTICAST_GROUP = "239.1.1.1"

MULTICAST_PORT = 50000

# Time between discovery announcements
ANNOUNCE_INTERVAL = 3

# Remove a peer if no announcement is received
PEER_TIMEOUT = 10

# Maximum time-to-live for multicast packets
MULTICAST_TTL = 1

# UDP port reserved for direct peer communication
CHAT_PORT = 50001
SIP_PORT = 50002