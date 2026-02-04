"""Fichier pour déterminer les structures des données saisies dans la db"""

from enum import Enum


class EntretienType(str, Enum):
    VIDANGE = "VIDANGE"
    PNEUS = "PNEUS"
    FREINS = "FREINS"
    REVISION = "REVISION"
    CONTROLE_TECHNIQUE = "CONTROLE_TECHNIQUE"


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    DRIVER = "DRIVER"
