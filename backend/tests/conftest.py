import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.database.session import engine


@pytest.fixture(autouse=True)
async def _dispose_engine_per_loop():
    yield
    await engine.dispose()
