# __init__.py

import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

__version__ = data["project"]["version"]

# Main module file, imports the

from .process_ambience_data import AmBIENCeDataset
from .process_ambience_data import ABMDataset
from .process_ambience_definitions import ABMDefinitions
