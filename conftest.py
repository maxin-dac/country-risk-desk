"""Configuration pytest : ajoute le répertoire projet au sys.path."""
import sys
import pathlib


root = pathlib.Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
