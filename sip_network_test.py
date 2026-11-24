
import socket
import sys

from config import SIP_PORT, CHAT_PORT
from sip_messages import (
    create_invite,
    create_bye,
    parse_message,
    create_response
)
from session import SessionManager

# =================================
# RECEIVER: WAIT FOR INVITE AND BYE
# =================================

def listen_for_invite(email):

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("", SIP_PORT))

    session = SessionManager()

    print("SIP server started!")
    print("User:", email)
    print("Listening on port:", SIP_PORT)
    print("Current state:", session.get_state())
    print("Waiting for requests...\n")

    try:
        while True:

            data, address = server.recvfrom(65535)

            try:
                request = parse_message(data)
            except ValueError as error:
                print("Invalid message:", error)
                continue

            start_line = request["start_line"]
            call_id = request["headers"].get("call-id", "")

            # -------------------------
            # INCOMING INVITE
            # -------------------------

            if start_line.startswith("INVITE "):

                destination = request["headers"].get("to", "")

                if email.lower() not in destination.lower():
                    print("INVITE is not addressed to this user.")
                    continue

                sender = request["headers"].get("from", "Unknown")

                if not call_id:
                    print("INVITE has no Call-ID.")
                    continue

                print("\nIncoming connection request!")
                print("From:", sender)
                print("Call-ID:", call_id)
                print("Sender IP:", address[0])

                accepted = session.receive_call(sender, call_id)

                if not accepted:
                    response = create_response(
                        request, 486, "Busy Here"
                    )

                    server.sendto(response, address)
                    print("486 Busy Here sent!")
                    continue

                session.accept_call()

                response = create_response(
                    request, 200, "OK"
                )

                server.sendto(response, address)

                print("200 OK sent successfully!")
                print("Current state:", session.get_state())

            # -------------------------
            # INCOMING BYE
            # -------------------------

            elif start_line.startswith("BYE "):

                print("\nBYE request received!")

                if (
                    session.get_state() == "CONNECTED"
                    and call_id == session.call_id
                ):

                    response = create_response(
                        request, 200, "OK"
                    )

                    session.end_call()

                    server.sendto(response, address)

                    print("200 OK sent for BYE!")
                    print("Session terminated.")
                    print("Current state:", session.get_state())

                else:

                    response = create_response(
                        request, 481, "Call Does Not Exist"
                    )

                    server.sendto(response, address)

                    print("Invalid or unknown session.")

            else:
                print("Unsupported request:", start_line)

    except KeyboardInterrupt:
        print("\nSIP server stopped.")

    finally:
        server.close()

# =================================
# SENDER: INVITE AND BYE
# =================================

def send_invite(from_email, to_email, target_ip):

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)

    try:
        client.connect((target_ip, SIP_PORT))
        local_ip = client.getsockname()[0]

        invite = create_invite(
            from_email=from_email,
            to_email=to_email,
            ip=local_ip,
            port=CHAT_PORT
        )

        print("Sending INVITE to:", target_ip)

        client.send(invite)

        print("INVITE sent successfully!")
        print("Waiting for response...\n")

        data = client.recv(65535)
        response = parse_message(data)

        print("Response received:")
        print(response["start_line"])

        request = parse_message(invite)

        expected_call_id = request["headers"].get("call-id")
        received_call_id = response["headers"].get("call-id")

        if received_call_id != expected_call_id:
            print("Error: Call-ID does not match.")
            return

        status = response["start_line"]

        if status == "SIP/2.0 486 Busy Here":
            print("User is BUSY. Try again later.")
            return

        if status != "SIP/2.0 200 OK":
            print("Connection request was not accepted.")
            return

        print("\nConnection request accepted!")
        print("You are now CONNECTED.")

        input("\nPress ENTER to end the call...")

        # -------------------------
        # SEND BYE
        # -------------------------

        bye = create_bye(
            from_email=from_email,
            to_email=to_email,
            call_id=expected_call_id,
            ip=local_ip,
            port=CHAT_PORT
        )

        print("\nSending BYE...")
        client.send(bye)

        data = client.recv(65535)
        bye_response = parse_message(data)

        print("Response received:")
        print(bye_response["start_line"])

        bye_call_id = bye_response["headers"].get("call-id")

        if bye_call_id != expected_call_id:
            print("Error: BYE Call-ID does not match.")
            return

        if bye_response["start_line"] == "SIP/2.0 200 OK":
            print("\nCall ended successfully!")
            print("Session terminated.")

        else:
            print("Could not confirm call termination.")

    except socket.timeout:
        print("No response received. Request timed out.")

    except (OSError, ValueError) as error:
        print("Communication error:", error)

    finally:
        client.close()

# =================================
# MAIN
# =================================

if len(sys.argv) < 2:

    print("Usage:")
    print("Receiver: python sip_network_test.py listen email")
    print("Sender:   python sip_network_test.py call from_email to_email target_ip")
    sys.exit(1)

mode = sys.argv[1].lower()

if mode == "listen" and len(sys.argv) == 3:

    listen_for_invite(sys.argv[2])

elif mode == "call" and len(sys.argv) == 5:

    send_invite(
        from_email=sys.argv[2],
        to_email=sys.argv[3],
        target_ip=sys.argv[4]
    )

else:
    print("Invalid arguments.")
    print("Receiver: python sip_network_test.py listen email")
    print("Sender: python sip_network_test.py call from_email to_email target_ip")