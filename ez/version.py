from importlib.metadata import version
from pathlib import Path
import tomllib


_project = Path(__file__).resolve().parents[1] / "pyproject.toml"
if _project.is_file():
    __version__ = tomllib.loads(_project.read_text(encoding="utf-8"))["project"]["version"]
else:
    __version__ = version("ez")