""" Fichier pour déterminer les structures des données saisies dans la db """

from enum import Enum

class EntretienType(str, Enum):
    VIDANGE = "Vidange"
    PNEUS = "Pneus"
    FREINS = "Freins"
    REVISION = "Révision"
    CONTROLE_TECHNIQUE = "Contrôle technique"