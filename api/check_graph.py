import torch
from pathlib import Path

GRAPH_PATH = Path(
    "models/distilbert_gat/deployment/graph_data.pt"
)

print("=" * 60)
print("PHISHGUARD AI - GRAPH CHECK")
print("=" * 60)

print("Graph path:")
print(GRAPH_PATH.resolve())

print("\nExists:")
print(GRAPH_PATH.exists())

if not GRAPH_PATH.exists():
    raise FileNotFoundError(
        "graph_data.pt not found."
    )

graph = torch.load(
    GRAPH_PATH,
    map_location="cpu",
    weights_only=False
)

print("\nGraph:")
print(graph)

print("\nNumber of nodes:")
print(graph.num_nodes)

print("\nNumber of edges:")
print(graph.edge_index.shape[1])

print("\nEdge index shape:")
print(graph.edge_index.shape)

print("\nEdge type shape:")
print(graph.edge_type.shape)

print("\nLabels shape:")
print(graph.y.shape)

print("\n✓ Graph loaded successfully.")