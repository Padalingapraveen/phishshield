import torch

from transformers import (
    AutoTokenizer,
    AutoModel
)


class DistilBERTEmbedder:

    def __init__(
        self,
        tokenizer_path,
        model_name="distilbert-base-uncased"
    ):

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"Loading DistilBERT on {self.device}"
        )

        # Load YOUR saved tokenizer
        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                str(tokenizer_path)
            )
        )

        print("Tokenizer loaded.")

        # Load the BASE DistilBERT encoder
        self.model = (
            AutoModel.from_pretrained(
                model_name
            )
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        print(
            "DistilBERT model loaded."
        )

    def create_embedding(
        self,
        text
    ):

        encoded = self.tokenizer(
            [text],
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )

        encoded = {
            key: value.to(self.device)
            for key, value in encoded.items()
        }

        with torch.no_grad():

            outputs = self.model(
                **encoded
            )

            token_embeddings = (
                outputs.last_hidden_state
            )

            attention_mask = (
                encoded["attention_mask"]
                .unsqueeze(-1)
                .expand(
                    token_embeddings.size()
                )
                .float()
            )

            summed = torch.sum(
                token_embeddings *
                attention_mask,
                dim=1
            )

            counts = torch.clamp(
                attention_mask.sum(dim=1),
                min=1e-9
            )

            embedding = (
                summed / counts
            )

        return embedding.cpu()