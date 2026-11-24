
from rtp import RTPPacket, parse_packet


# Create RTP packet generator
sender = RTPPacket()

# Test messages
messages = [
    "Hello Anfel!",
    "Bonjour!",
    "مرحبا أنفال ❤️"
]

for text in messages:

    print("\nOriginal message:", text)

    # Create RTP packet
    packet = sender.create_packet(text)

    print("Packet size:", len(packet), "bytes")

    # Parse received packet
    received = parse_packet(packet)

    print("RTP Version:", received["version"])
    print("Payload Type:", received["payload_type"])
    print("Sequence Number:", received["sequence_number"])
    print("Timestamp:", received["timestamp"])
    print("SSRC:", received["ssrc"])
    print("Received message:", received["message"])

    assert received["message"] == text

print("\nAll RTP tests passed!")
