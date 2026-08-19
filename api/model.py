import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import GATConv


class DistilBERTGAT(nn.Module):

    def __init__(
        self,
        input_dim=768,
        gat_hidden=128,
        gat_output=64,
        num_classes=2,
        heads=4,
        dropout=0.2
    ):
        super().__init__()

        self.gat1 = GATConv(
            in_channels=input_dim,
            out_channels=gat_hidden,
            heads=heads,
            dropout=dropout
        )

        self.gat2 = GATConv(
            in_channels=gat_hidden * heads,
            out_channels=gat_output,
            heads=1,
            concat=False,
            dropout=dropout
        )

        fusion_dim = input_dim + gat_output

        self.classifier = nn.Sequential(

            nn.Linear(
                fusion_dim,
                256
            ),

            nn.ReLU(),

            nn.Dropout(dropout),

            nn.Linear(
                256,
                64
            ),

            nn.ReLU(),

            nn.Dropout(dropout),

            nn.Linear(
                64,
                num_classes
            )
        )

        self.dropout = dropout

    def forward(
        self,
        x,
        edge_index
    ):

        original_x = x

        x = self.gat1(
            x,
            edge_index
        )

        x = F.elu(x)

        x = F.dropout(
            x,
            p=self.dropout,
            training=self.training
        )

        x = self.gat2(
            x,
            edge_index
        )

        x = F.elu(x)

        fused = torch.cat(
            [
                original_x,
                x
            ],
            dim=1
        )

        return self.classifier(fused)


def load_gat_model(model_path):

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Device: {device}")

    checkpoint = torch.load(
        model_path,
        map_location=device,
        weights_only=False
    )

    print("\nCheckpoint configuration:")

    print(
        "input_dim:",
        checkpoint["input_dim"]
    )

    print(
        "gat_hidden:",
        checkpoint["gat_hidden"]
    )

    print(
        "gat_output:",
        checkpoint["gat_output"]
    )

    print(
        "heads:",
        checkpoint["heads"]
    )

    print(
        "num_classes:",
        checkpoint["num_classes"]
    )

    print(
        "dropout:",
        checkpoint["dropout"]
    )

    model = DistilBERTGAT(
        input_dim=checkpoint["input_dim"],
        gat_hidden=checkpoint["gat_hidden"],
        gat_output=checkpoint["gat_output"],
        num_classes=checkpoint["num_classes"],
        heads=checkpoint["heads"],
        dropout=checkpoint["dropout"]
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)

    model.eval()

    return model, checkpoint, device