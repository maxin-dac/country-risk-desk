"""Configuration pytest : ajoute le répertoire projet au sys.path."""
import sys
import pathlib

# Ajouter la racine du projet au sys.path pour que 'src' soit trouvable
root = pathlib.Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
