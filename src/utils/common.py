import tomllib
from pathlib import Path


def get_app_version():
    with open(Path(__file__).resolve().parent.parent.parent / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["tool"]["poetry"]["version"]
