from pathlib import Path

# Project root (or the onefile extraction directory at runtime)
BASE_DIR = Path(__file__).resolve().parent.parent


def resolve_asset(path):
    """Resolve bundled asset paths; absolute paths pass through unchanged."""
    path = Path(path)
    return path if path.is_absolute() else BASE_DIR / path
