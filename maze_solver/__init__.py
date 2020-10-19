from importlib.metadata import version
from pathlib import Path

__version__ = version('maze-solver')

_ROOT = Path(__file__).parent.parent


def get_asset_path(*relative_path: str) -> Path:
    full_path = _ROOT / 'assets'
    for sub_path in relative_path:
        full_path = full_path / sub_path
    return full_path
