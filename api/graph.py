from collections import defaultdict
import re

import pandas as pd
import torch
from torch_geometric.data import Data


class ReferenceGraph:

    def __init__(
        self,
        graph_path,
        reference_csv,
        embeddings_path
    ):

        print("Loading reference graph...")

        # =====================================================
        # LOAD REFERENCE GRAPH
        # =====================================================

        self.graph = torch.load(
            graph_path,
            map_location="cpu",
            weights_only=False
        )

        self.reference_embeddings = torch.load(
            embeddings_path,
            map_location="cpu",
            weights_only=False
        )

        self.reference_df = pd.read_csv(
            reference_csv
        )

        print(
            f"Reference nodes: "
            f"{self.graph.num_nodes}"
        )

        print(
            f"Reference edges: "
            f"{self.graph.edge_index.shape[1]}"
        )

        print(
            f"Reference embeddings: "
            f"{self.reference_embeddings.shape}"
        )

        # =====================================================
        # BUILD LOOKUP INDEXES ONCE
        # =====================================================

        self._build_entity_maps()

        print("[OK] Reference graph ready.")

    # =========================================================
    # EMAIL EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_email(value):

        if value is None:
            return ""

        text = str(value).strip().lower()

        if not text:
            return ""

        match = re.search(
            r"[\w.+-]+@[\w.-]+\.\w+",
            text
        )

        if match:
            return match.group(0)

        return text

    # =========================================================
    # DOMAIN EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_domains(value):

        if value is None:
            return set()

        text = str(value).lower()

        if not text:
            return set()

        domains = set()

        # -----------------------------------------------------
        # Domains from email addresses
        # -----------------------------------------------------

        email_domains = re.findall(
            r"[\w.+-]+@([\w.-]+\.\w+)",
            text
        )

        for domain in email_domains:

            domain = domain.lower().strip()

            if domain:
                domains.add(domain)

        # -----------------------------------------------------
        # Domains from URLs
        # -----------------------------------------------------

        url_domains = re.findall(
            r"https?://([^/\s/:]+)",
            text
        )

        for domain in url_domains:

            domain = domain.lower().strip()

            if domain:
                domains.add(domain)

        return domains

    # =========================================================
    # BUILD ENTITY INDEXES
    # =========================================================

    def _build_entity_maps(self):

        print(
            "Building entity indexes..."
        )

        self.sender_map = defaultdict(list)

        self.receiver_map = defaultdict(list)

        self.domain_map = defaultdict(list)

        # -----------------------------------------------------
        # Iterate once through reference dataset
        # -----------------------------------------------------

        for idx, row in self.reference_df.iterrows():

            sender = self._extract_email(
                row.get("sender", "")
            )

            receiver = self._extract_email(
                row.get("receiver", "")
            )

            # -------------------------------------------------
            # Sender index
            # -------------------------------------------------

            if sender:

                self.sender_map[
                    sender
                ].append(idx)

            # -------------------------------------------------
            # Receiver index
            # -------------------------------------------------

            if receiver:

                self.receiver_map[
                    receiver
                ].append(idx)

            # -------------------------------------------------
            # Domain index
            # -------------------------------------------------

            text = " ".join(
                [
                    str(row.get("sender", "")),
                    str(row.get("receiver", "")),
                    str(row.get("subject", "")),
                    str(row.get("body", ""))
                ]
            )

            domains = self._extract_domains(
                text
            )

            for domain in domains:

                self.domain_map[
                    domain
                ].append(idx)

        print(
            f"Sender entities: "
            f"{len(self.sender_map)}"
        )

        print(
            f"Receiver entities: "
            f"{len(self.receiver_map)}"
        )

        print(
            f"Domain entities: "
            f"{len(self.domain_map)}"
        )

    # =========================================================
    # FIND LOCAL NEIGHBORS
    # =========================================================

    def find_neighbors(
        self,
        sender,
        receiver,
        domains,
        max_neighbors=10
    ):

        sender = self._extract_email(
            sender
        )

        receiver = self._extract_email(
            receiver
        )

        # -----------------------------------------------------
        # Use set for O(1) duplicate checking
        # -----------------------------------------------------

        selected = set()

        neighbors = []

        edge_types = []

        # =====================================================
        # PRIORITY 1: SAME SENDER
        # =====================================================

        sender_nodes = self.sender_map.get(
            sender,
            []
        )

        for node in sender_nodes:

            if node in selected:
                continue

            selected.add(node)

            neighbors.append(node)

            edge_types.append(0)

            if len(neighbors) >= max_neighbors:
                return neighbors, edge_types

        # =====================================================
        # PRIORITY 2: SAME RECEIVER
        # =====================================================

        receiver_nodes = self.receiver_map.get(
            receiver,
            []
        )

        for node in receiver_nodes:

            if node in selected:
                continue

            selected.add(node)

            neighbors.append(node)

            edge_types.append(1)

            if len(neighbors) >= max_neighbors:
                return neighbors, edge_types

        # =====================================================
        # PRIORITY 3: SHARED DOMAIN
        # =====================================================

        # Sort domains for deterministic inference
        for domain in sorted(domains):

            domain_nodes = self.domain_map.get(
                domain,
                []
            )

            for node in domain_nodes:

                if node in selected:
                    continue

                selected.add(node)

                neighbors.append(node)

                edge_types.append(2)

                if len(neighbors) >= max_neighbors:
                    return neighbors, edge_types

        return neighbors, edge_types

    # =========================================================
    # CREATE LOCAL INFERENCE GRAPH
    # =========================================================

    def create_inference_graph(
        self,
        new_embedding,
        sender,
        receiver,
        domains,
        max_neighbors=10
    ):

        # -----------------------------------------------------
        # Find relevant reference nodes
        # -----------------------------------------------------

        neighbors, edge_types = (
            self.find_neighbors(
                sender=sender,
                receiver=receiver,
                domains=domains,
                max_neighbors=max_neighbors
            )
        )

        # =====================================================
        # NEW EMAIL EMBEDDING
        # =====================================================

        new_embedding = (
            new_embedding
            .detach()
            .cpu()
            .reshape(1, -1)
            .float()
        )

        # =====================================================
        # NO NEIGHBORS
        # =====================================================

        if not neighbors:

            empty_edges = torch.empty(
                (2, 0),
                dtype=torch.long
            )

            graph = Data(
                x=new_embedding,
                edge_index=empty_edges,
                num_nodes=1
            )

            return (
                graph,
                [],
                []
            )

        # =====================================================
        # SELECT ONLY NEIGHBOR EMBEDDINGS
        # =====================================================

        neighbor_embeddings = (
            self.reference_embeddings[
                neighbors
            ]
            .detach()
            .cpu()
            .float()
        )

        # =====================================================
        # GRAPH FEATURES
        #
        # [neighbor1]
        # [neighbor2]
        # ...
        # [neighborN]
        # [new email]
        # =====================================================

        x = torch.cat(
            [
                neighbor_embeddings,
                new_embedding
            ],
            dim=0
        )

        # New email is always the final node
        new_node = len(neighbors)

        # =====================================================
        # CREATE BIDIRECTIONAL EDGES
        # =====================================================

        edges = []

        for local_index in range(
            len(neighbors)
        ):

            # Reference -> New Email
            edges.append(
                [
                    local_index,
                    new_node
                ]
            )

            # New Email -> Reference
            edges.append(
                [
                    new_node,
                    local_index
                ]
            )

        edge_index = torch.tensor(
            edges,
            dtype=torch.long
        ).t().contiguous()

        # =====================================================
        # CREATE LOCAL GRAPH
        # =====================================================

        graph = Data(
            x=x,
            edge_index=edge_index,
            num_nodes=x.shape[0]
        )

        return (
            graph,
            neighbors,
            edge_types
        )