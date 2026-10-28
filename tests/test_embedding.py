from pathlib import Path

from api.embedding import DistilBERTEmbedder
from api.preprocessing import create_model_text


TOKENIZER_PATH = Path(
    "models/distilbert_gat/deployment/tokenizer"
)


embedder = DistilBERTEmbedder(
    tokenizer_path=TOKENIZER_PATH
)


sender = "Security Team <security@example.com>"

receiver = "user@gmail.com"

subject = "Verify your account"

body = """
Your account has been suspended.
Click https://example.com/verify
to restore access.
"""


text = create_model_text(
    sender,
    receiver,
    subject,
    body
)


print("\nModel input:")
print(text)


embedding = embedder.create_embedding(
    text
)


print("\nEmbedding shape:")
print(embedding.shape)


print("\nEmbedding dtype:")
print(embedding.dtype)


print("\nFirst 10 values:")
print(embedding[:10])


assert embedding.shape == (1, 768)


print(
    "\n[OK] Mean-pooled DistilBERT embedding "
    "created successfully."
)