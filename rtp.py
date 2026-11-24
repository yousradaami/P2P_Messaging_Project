
import struct
import time


# =================================
# RTP CONFIGURATION
# =================================

RTP_VERSION = 2
RTP_PAYLOAD_TYPE = 96
RTP_HEADER_SIZE = 12


# =================================
# RTP PACKET CREATION
# =================================

class RTPPacket:

    def __init__(self, payload_type=RTP_PAYLOAD_TYPE):

        self.version = RTP_VERSION
        self.payload_type = payload_type
        self.sequence_number = 0
        self.timestamp = 0
        self.ssrc = 0

    def create_packet(self, message):

        # Convert text into UTF-8 bytes
        payload = message.encode("utf-8")

        # Update RTP fields
        self.sequence_number = (
            self.sequence_number + 1
        ) % 65536

        self.timestamp = int(time.time() * 1000) % (2 ** 32)

        # Generate a random synchronization source ID
        if self.ssrc == 0:
            import random
            self.ssrc = random.randint(1, 2 ** 32 - 1)

        # Build RTP header
        first_byte = (self.version << 6)

        second_byte = self.payload_type & 0x7F

        header = struct.pack(
            "!BBHII",
            first_byte,
            second_byte,
            self.sequence_number,
            self.timestamp,
            self.ssrc
        )

        return header + payload


# =================================
# RTP PACKET PARSING
# =================================

def parse_packet(packet):

    if len(packet) < RTP_HEADER_SIZE:
        raise ValueError("Invalid RTP packet: header too short.")

    # Read RTP header
    first_byte, second_byte, sequence, timestamp, ssrc = struct.unpack(
        "!BBHII",
        packet[:RTP_HEADER_SIZE]
    )

    version = first_byte >> 6

    if version != RTP_VERSION:
        raise ValueError("Unsupported RTP version.")

    # Check padding, extension and CSRC count
    padding = (first_byte >> 5) & 1
    extension = (first_byte >> 4) & 1
    csrc_count = first_byte & 0x0F

    if extension or csrc_count != 0:
        raise ValueError("RTP extensions and CSRC are not supported.")

    payload_type = second_byte & 0x7F

    if payload_type != RTP_PAYLOAD_TYPE:
        raise ValueError("Unsupported RTP payload type.")

    payload = packet[RTP_HEADER_SIZE:]

    if padding:
        if not payload:
            raise ValueError("Invalid RTP padding.")

        padding_size = payload[-1]

        if padding_size == 0 or padding_size > len(payload):
            raise ValueError("Invalid RTP padding size.")

        payload = payload[:-padding_size]

    # Decode UTF-8 message
    try:
        message = payload.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Payload is not valid UTF-8.")

    return {
        "version": version,
        "payload_type": payload_type,
        "sequence_number": sequence,
        "timestamp": timestamp,
        "ssrc": ssrc,
        "message": message
    }
