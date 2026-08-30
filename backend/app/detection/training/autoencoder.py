from pathlib import Path
from datetime import datetime, timezone

import numpy as np


class AutoencoderModel:
    def __init__(self, input_dim: int, encoding_dim: int = 16, hidden_dims: list[int] | None = None) -> None:
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.hidden_dims = hidden_dims or [64, 32]
        self.model = None
        self.threshold: float | None = None
        self.config: dict = {}

    def build(self) -> None:
        import torch
        from torch import nn

        layers: list[nn.Module] = []
        prev = self.input_dim
        for h in self.hidden_dims:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(h))
            prev = h
        layers.append(nn.Linear(prev, self.encoding_dim))
        encoder = nn.Sequential(*layers)

        decoder_layers: list[nn.Module] = []
        prev = self.encoding_dim
        for h in reversed(self.hidden_dims):
            decoder_layers.append(nn.Linear(prev, h))
            decoder_layers.append(nn.ReLU())
            decoder_layers.append(nn.BatchNorm1d(h))
            prev = h
        decoder_layers.append(nn.Linear(prev, self.input_dim))
        decoder = nn.Sequential(*decoder_layers)

        self.model = nn.Sequential(encoder, decoder)

    def train(self, X_train: np.ndarray, X_val: np.ndarray | None = None, epochs: int = 100, batch_size: int = 256, learning_rate: float = 1e-3) -> dict:
        import torch
        from torch import nn

        if self.model is None:
            self.build()

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)

        X_tensor = torch.FloatTensor(X_train).to(device)
        dataset = torch.utils.data.TensorDataset(X_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        history: list[float] = []
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0.0
            for batch in loader:
                optimizer.zero_grad()
                output = self.model(batch[0])
                loss = criterion(output, batch[0])
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            avg_loss = total_loss / len(loader)
            history.append(avg_loss)

        if X_val is not None:
            self.calculate_threshold(X_val)
        else:
            self.calculate_threshold(X_train)

        self.config = {
            "input_dim": self.input_dim,
            "encoding_dim": self.encoding_dim,
            "hidden_dims": self.hidden_dims,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "training_loss_history": history[-10:],
        }
        return {"final_loss": history[-1], "threshold": self.threshold}

    def calculate_threshold(self, X_val: np.ndarray, percentile: float = 95.0) -> float:
        import torch

        if self.model is None:
            raise RuntimeError("Model not built")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_val).to(device)
            reconstructed = self.model(X_tensor).cpu().numpy()
        errors = np.mean((X_val - reconstructed) ** 2, axis=1)
        self.threshold = float(np.percentile(errors, percentile))
        return self.threshold

    def predict(self, X: np.ndarray) -> dict:
        import torch

        if self.model is None or self.threshold is None:
            raise RuntimeError("Model not trained or threshold not set")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(device)
            reconstructed = self.model(X_tensor).cpu().numpy()
        errors = np.mean((X - reconstructed) ** 2, axis=1)
        return {
            "anomaly_score": errors,
            "threshold": self.threshold,
            "is_anomaly": errors > self.threshold,
        }

    def save(self, path: str) -> None:
        import torch

        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state": self.model.state_dict() if self.model else None,
            "config": self.config,
            "input_dim": self.input_dim,
            "encoding_dim": self.encoding_dim,
            "hidden_dims": self.hidden_dims,
            "threshold": self.threshold,
        }, model_path)

    @classmethod
    def load(cls, path: str) -> "AutoencoderModel":
        import torch

        data = torch.load(path, weights_only=False)
        obj = cls(input_dim=data["input_dim"], encoding_dim=data["encoding_dim"], hidden_dims=data["hidden_dims"])
        obj.build()
        if data["model_state"]:
            obj.model.load_state_dict(data["model_state"])
        obj.threshold = data["threshold"]
        obj.config = data["config"]
        return obj
