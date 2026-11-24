
from database import register_user, login_user

# Test account
email = "test@example.com"
password = "TestPass123"

# Test registration
success, message = register_user(email, password)
print("Registration:", message)

# Test login with correct password
if login_user(email, password):
    print("Login: Successful!")
else:
    print("Login: Failed!")

# Test login with incorrect password
if login_user(email, "WrongPassword"):
    print("Security Test: Failed!")
else:
    print("Security Test: Passed!")
