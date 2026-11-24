
import uuid


# ==============================
# SIP-LIKE MESSAGE BUILDER
# ==============================

def build_message(start_line, headers, body=""):
    """
    Build a SIP-like message using UTF-8.
    """

    body_bytes = body.encode("utf-8")

    headers = headers.copy()
    headers["Content-Length"] = str(len(body_bytes))

    message = start_line + "\r\n"

    for name, value in headers.items():
        message += f"{name}: {value}\r\n"

    message += "\r\n"
    message_bytes = message.encode("utf-8") + body_bytes

    return message_bytes


# ==============================
# SIP-LIKE MESSAGE PARSER
# ==============================

def parse_message(data):
    """
    Parse a SIP-like message received as bytes.
    """

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Message is not valid UTF-8.")

    if "\r\n\r\n" not in text:
        raise ValueError("Invalid message: missing header separator.")

    header_part, body = text.split("\r\n\r\n", 1)

    lines = header_part.split("\r\n")

    if not lines or not lines[0]:
        raise ValueError("Missing start line.")

    start_line = lines[0]
    headers = {}

    for line in lines[1:]:
        if ":" not in line:
            raise ValueError(f"Invalid header: {line}")

        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()

    content_length = headers.get("content-length")

    if content_length is None:
        raise ValueError("Missing Content-Length header.")

    try:
        expected_length = int(content_length)
    except ValueError:
        raise ValueError("Invalid Content-Length.")

    body_bytes = body.encode("utf-8")

    if len(body_bytes) != expected_length:
        raise ValueError("Content-Length does not match the body.")

    return {
        "start_line": start_line,
        "headers": headers,
        "body": body
    }


# ==============================
# CREATE INVITE
# ==============================

def create_invite(from_email, to_email, ip, port):
    """
    Create an INVITE request with a simple SDP-like description.
    """

    call_id = str(uuid.uuid4())

    start_line = f"INVITE sip:{to_email} SIP/2.0"

    headers = {
        "Via": f"SIP/2.0/UDP {ip}:{port}",
        "From": f"<sip:{from_email}>",
        "To": f"<sip:{to_email}>",
        "Call-ID": call_id,
        "CSeq": "1 INVITE",
        "Contact": f"<sip:{from_email}@{ip}:{port}>",
        "Content-Type": "application/sdp"
    }

    body = (
        "v=0\r\n"
        f"o={from_email} 1 1 IN IP4 {ip}\r\n"
        "s=P2P Messaging Session\r\n"
        f"c=IN IP4 {ip}\r\n"
        "t=0 0\r\n"
        f"m=message {port} RTP/AVP 96\r\n"
        "a=charset:UTF-8\r\n"
    )

    return build_message(start_line, headers, body)


# ==============================
# CREATE RESPONSE
# ==============================

def create_response(request_data, status_code, reason):
    """
    Create a response to an INVITE request.
    """

    request_headers = request_data["headers"]

    start_line = f"SIP/2.0 {status_code} {reason}"

    headers = {
        "Via": request_headers.get("via", ""),
        "From": request_headers.get("from", ""),
        "To": request_headers.get("to", ""),
        "Call-ID": request_headers.get("call-id", ""),
        "CSeq": request_headers.get("cseq", "")
    }

    return build_message(start_line, headers)


# ==============================
# CREATE BYE
# ==============================

def create_bye(from_email, to_email, call_id, ip, port):
    """
    Create a BYE request to terminate a session.
    """

    start_line = f"BYE sip:{to_email} SIP/2.0"

    headers = {
        "Via": f"SIP/2.0/UDP {ip}:{port}",
        "From": f"<sip:{from_email}>",
        "To": f"<sip:{to_email}>",
        "Call-ID": call_id,
        "CSeq": "2 BYE"
    }

    return build_message(start_line, headers)
