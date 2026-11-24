
from sip_messages import (
    create_invite,
    parse_message,
    create_response,
    create_bye
)


# 1. Create an INVITE request
invite = create_invite(
    from_email="yousra@example.com",
    to_email="anfel@example.com",
    ip="192.168.56.1",
    port=50001
)

print("========== INVITE MESSAGE ==========")
print(invite.decode("utf-8"))


# 2. Parse the INVITE request
request = parse_message(invite)

print("\n========== PARSED MESSAGE ==========")
print("Start line:", request["start_line"])
print("Call-ID:", request["headers"]["call-id"])
print("Content-Type:", request["headers"]["content-type"])
print("Session description:")
print(request["body"])


# 3. Create a 200 OK response
response = create_response(
    request,
    200,
    "OK"
)

print("\n========== RESPONSE MESSAGE ==========")
print(response.decode("utf-8"))


# 4. Parse and verify the response
parsed_response = parse_message(response)
print("Response:", parsed_response["start_line"])


# 5. Create a BYE request
bye = create_bye(
    from_email="yousra@example.com",
    to_email="anfel@example.com",
    call_id=request["headers"]["call-id"],
    ip="192.168.56.1",
    port=50001
)

print("\n========== BYE MESSAGE ==========")
print(bye.decode("utf-8"))

print("\nAll SIP-like tests passed!")
