import json
from pathlib import Path
from app.detection.features.feature_schema import FEATURE_SCHEMA, PROTOCOL_MAP


class PreprocessorConfig:
    def __init__(self) -> None:
        self.feature_names: list[str] = list(FEATURE_SCHEMA)
        self.protocol_map: dict[str, int] = dict(PROTOCOL_MAP)
        self.scaling_method: str = "standard"
        self.numeric_defaults: dict[str, float] = {}

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "feature_names": self.feature_names,
                "protocol_map": self.protocol_map,
                "scaling_method": self.scaling_method,
                "numeric_defaults": self.numeric_defaults,
            }, f, indent=2)

    @classmethod
    def load(cls, path: str) -> "PreprocessorConfig":
        with open(path) as f:
            data = json.load(f)
        obj = cls()
        obj.feature_names = data.get("feature_names", list(FEATURE_SCHEMA))
        obj.protocol_map = data.get("protocol_map", dict(PROTOCOL_MAP))
        obj.scaling_method = data.get("scaling_method", "standard")
        obj.numeric_defaults = data.get("numeric_defaults", {})
        return obj
