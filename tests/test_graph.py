from pathlib import Path

import torch

from api.graph import ReferenceGraph


BASE = Path(
    "models/distilbert_gat/deployment"
)


GRAPH_PATH = (
    BASE / "graph_data.pt"
)

EMBEDDINGS_PATH = (
    BASE / "train_embeddings.pt"
)

REFERENCE_PATH = (
    BASE / "reference_emails.csv"
)


reference_graph = ReferenceGraph(
    graph_path=GRAPH_PATH,
    reference_csv=REFERENCE_PATH,
    embeddings_path=EMBEDDINGS_PATH
)


sender = "security@example.com"

receiver = "user@gmail.com"

domains = [
    "example.com",
    "gmail.com"
]


neighbors, edge_types = (
    reference_graph.find_neighbors(
        sender=sender,
        receiver=receiver,
        domains=domains
    )
)


print("\n" + "=" * 60)

print("GRAPH INFERENCE TEST")

print("=" * 60)

print(
    "Neighbors found:",
    len(neighbors)
)

print(
    "Neighbor IDs:",
    neighbors[:20]
)

print(
    "Edge types:",
    edge_types[:20]
)


# Create a fake 768-dimensional embedding
# ONLY for testing graph construction.

fake_embedding = torch.randn(
    768
)


inference_graph, neighbors, edge_types = (
    reference_graph.create_inference_graph(
        new_embedding=fake_embedding,
        sender=sender,
        receiver=receiver,
        domains=domains
    )
)


print("\nInference graph:")

print(inference_graph)

print(
    "\nNew node ID:",
    inference_graph.num_nodes - 1
)

print(
    "Total nodes:",
    inference_graph.num_nodes
)

print(
    "Total edges:",
    inference_graph.edge_index.shape[1]
)

print("\n[OK] Graph inference construction works.")