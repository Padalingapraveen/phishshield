from transformers import AutoTokenizer

TOKENIZER_PATH = (
    "models/distilbert_gat/deployment/tokenizer"
)

print("=" * 60)
print("PHISHGUARD AI - TOKENIZER CHECK")
print("=" * 60)

tokenizer = AutoTokenizer.from_pretrained(
    TOKENIZER_PATH,
    local_files_only=True
)

text = """
Your account has been suspended.
Click the link to verify your account.
"""

tokens = tokenizer(
    text,
    truncation=True,
    max_length=512
)

print("Tokenizer loaded successfully.")

print("\nNumber of tokens:")
print(len(tokens["input_ids"]))

print("\nFirst tokens:")
print(
    tokenizer.convert_ids_to_tokens(
        tokens["input_ids"][:20]
    )
)

print("\n✓ Tokenizer working.")