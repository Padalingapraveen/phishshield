from pathlib import Path

import torch
import torch.nn.functional as F

from api.model import load_gat_model
from api.embedding import DistilBERTEmbedder
from api.preprocessing import (
    preprocess_email,
    create_model_text
)
from api.graph import ReferenceGraph
import logging

logger = logging.getLogger(__name__)


from api.config import (
    MODEL_PATH,
    GRAPH_PATH,
    EMBEDDINGS_PATH,
    REFERENCE_PATH,
    TOKENIZER_PATH,
    CLASSIFICATION_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
    RISK_HIGH_THRESHOLD,
    RISK_CRITICAL_THRESHOLD
)


class PhishGuardPredictor:

    def __init__(self):

        print("=" * 60)
        print("PHISHGUARD AI - INITIALIZING")
        print("=" * 60)

        print(
            f"\nClassification threshold: "
            f"{CLASSIFICATION_THRESHOLD:.2f}"
        )

        print(
            "Risk levels: "
            "LOW < 0.47 | "
            "MEDIUM 0.47-0.59 | "
            "HIGH 0.60-0.79 | "
            "CRITICAL >= 0.80"
        )

        # ----------------------------------------------------
        # 1. Load GAT
        # ----------------------------------------------------

        print("\n[1/3] Loading GAT...")

        (
            self.gat,
            self.checkpoint,
            self.device
        ) = load_gat_model(
            MODEL_PATH
        )

        # ----------------------------------------------------
        # 2. Load DistilBERT
        # ----------------------------------------------------

        print("\n[2/3] Loading DistilBERT...")

        self.embedder = DistilBERTEmbedder(
            tokenizer_path=TOKENIZER_PATH
        )

        # ----------------------------------------------------
        # 3. Load reference graph
        # ----------------------------------------------------

        print("\n[3/3] Loading reference graph...")

        self.reference_graph = ReferenceGraph(
            graph_path=GRAPH_PATH,
            reference_csv=REFERENCE_PATH,
            embeddings_path=EMBEDDINGS_PATH
        )

        print("\nPhishGuard predictor ready.")

    # ========================================================
    # RISK LEVEL
    # ========================================================

    @staticmethod
    def get_risk_level(
        phishing_probability
    ):

        probability = float(
            phishing_probability
        )

        if probability >= RISK_CRITICAL_THRESHOLD:

            return "CRITICAL"

        if probability >= RISK_HIGH_THRESHOLD:

            return "HIGH"

        if probability >= RISK_MEDIUM_THRESHOLD:

            return "MEDIUM"

        return "LOW"

    # ========================================================
    # PREDICTION
    # ========================================================

    def predict(
        self,
        sender,
        receiver,
        subject,
        body
    ):

        # Ensure strings and handle None gracefully
        sender = str(sender) if sender is not None else ""
        receiver = str(receiver) if receiver is not None else ""
        subject = str(subject) if subject is not None else ""
        body = str(body) if body is not None else ""

        try:
            # ----------------------------------------------------
            # Step 1: Preprocess email
            # ----------------------------------------------------

            entities = preprocess_email(
                sender=sender,
                receiver=receiver,
                subject=subject,
                body=body
            )

            # ----------------------------------------------------
            # Step 2: Create model input
            # ----------------------------------------------------

            text = create_model_text(
                sender=sender,
                receiver=receiver,
                subject=subject,
                body=body
            )

            # ----------------------------------------------------
            # Step 3: DistilBERT embedding
            # ----------------------------------------------------

            embedding = (
                self.embedder.create_embedding(
                    text
                )
            )

            # ----------------------------------------------------
            # Step 4: Create local inference graph
            # ----------------------------------------------------

            (
                inference_graph,
                neighbors,
                edge_types
            ) = self.reference_graph.create_inference_graph(
                new_embedding=embedding,
                sender=entities["sender_entity"],
                receiver=entities["receiver_entity"],
                domains=entities["domain_entities"]
            )

            # ----------------------------------------------------
            # Step 5: Move graph to model device
            # ----------------------------------------------------

            x = inference_graph.x.to(
                self.device
            )

            edge_index = (
                inference_graph.edge_index.to(
                    self.device
                )
            )

            # ----------------------------------------------------
            # Step 6: GAT inference
            # ----------------------------------------------------

            self.gat.eval()

            with torch.no_grad():

                logits = self.gat(
                    x,
                    edge_index
                )

                # New email is always the final node.
                new_node = (
                    inference_graph.num_nodes - 1
                )

                new_logits = (
                    logits[new_node]
                )

                probabilities = F.softmax(
                    new_logits,
                    dim=0
                )

            # ----------------------------------------------------
            # Step 7: Extract probabilities
            # ----------------------------------------------------

            non_phishing_probability = float(
                probabilities[0].item()
            )

            phishing_probability = float(
                probabilities[1].item()
            )

            # ----------------------------------------------------
            # Step 8: Production classification
            # ----------------------------------------------------

            predicted_label = int(
                phishing_probability
                >= CLASSIFICATION_THRESHOLD
            )

            if predicted_label == 1:

                label = "PHISHING"

            else:

                label = "NON-PHISHING"

            # ----------------------------------------------------
            # Step 9: Risk score
            # ----------------------------------------------------

            risk_score = (
                phishing_probability * 100.0
            )

            # ----------------------------------------------------
            # Step 10: Risk level
            # ----------------------------------------------------

            risk_level = self.get_risk_level(
                phishing_probability
            )

            # ----------------------------------------------------
            # Step 11: Return production response
            # ----------------------------------------------------

            return {

                "label":
                    label,

                "predicted_class":
                    predicted_label,

                "classification_threshold":
                    CLASSIFICATION_THRESHOLD,

                "phishing_probability":
                    phishing_probability,

                "non_phishing_probability":
                    non_phishing_probability,

                "risk_score":
                    risk_score,

                "risk_level":
                    risk_level,

                "graph_neighbors":
                    len(neighbors),

                "graph_edge_types":
                    edge_types,

                "sender_entity":
                    entities[
                        "sender_entity"
                    ],

                "receiver_entity":
                    entities[
                        "receiver_entity"
                    ],

                "domain_entities":
                    entities[
                        "domain_entities"
                    ]
            }

        except Exception as e:
            logger.error(f"Prediction failed for request involving sender {hash(sender)} and receiver {hash(receiver)}. Error: {str(e)}")
            raise
