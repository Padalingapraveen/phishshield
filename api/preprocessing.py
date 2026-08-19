import re


EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+\.\w+"
)

URL_PATTERN = re.compile(
    r"https?://([^/\s]+)"
)


def extract_email_entity(value: str) -> str:

    if not value:
        return ""

    match = EMAIL_PATTERN.search(value)

    if match:
        return match.group(0).lower()

    return value.strip().lower()


def extract_domain_from_email(value: str) -> str:

    email = extract_email_entity(value)

    if "@" not in email:
        return ""

    return email.split("@", 1)[1].lower()


def extract_domain_entities(
    sender: str,
    receiver: str,
    subject: str,
    body: str
):

    text = " ".join(
        [
            sender or "",
            receiver or "",
            subject or "",
            body or ""
        ]
    )

    domains = set()

    # Email domains
    emails = EMAIL_PATTERN.findall(text)

    for email in emails:

        if "@" in email:

            domain = (
                email
                .split("@", 1)[1]
                .lower()
            )

            domains.add(domain)

    # URL domains
    urls = URL_PATTERN.findall(text)

    for domain in urls:

        domains.add(
            domain.lower()
        )

    return sorted(domains)


def preprocess_email(
    sender: str,
    receiver: str,
    subject: str,
    body: str
):

    sender_entity = extract_email_entity(
        sender
    )

    receiver_entity = extract_email_entity(
        receiver
    )

    domain_entities = extract_domain_entities(
        sender,
        receiver,
        subject,
        body
    )

    return {
        "sender_entity": sender_entity,
        "receiver_entity": receiver_entity,
        "domain_entities": domain_entities
    }


def create_model_text(
    sender: str,
    receiver: str,
    subject: str,
    body: str
):

    return (
        f"sender: {sender} "
        f"receiver: {receiver} "
        f"subject: {subject} "
        f"body: {body}"
    )