from preprocessing import (
    preprocess_email,
    create_model_text
)


sender = "Security Team <security@example.com>"

receiver = "user@gmail.com"

subject = "Verify your account"

body = """
Your account has been suspended.
Click https://example.com/verify
to restore access.
"""


entities = preprocess_email(
    sender,
    receiver,
    subject,
    body
)

print("Entities:")
print(entities)

print("\nModel text:")
print(
    create_model_text(
        sender,
        receiver,
        subject,
        body
    )
)