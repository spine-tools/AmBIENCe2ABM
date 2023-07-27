# __init__.py

import importlib.metadata

__version__ = importlib.metadata.version("ambience2abm")

# Main module file, imports the

from .process_ambience_data import AmBIENCeDataset
from .process_ambience_data import ABMDataset
