"""Module de chargement de config/données, écrit avant que l'équipe
n'adopte pydantic. Personne ne sait exactement d'où viennent tous les
fichiers qu'il charge, donc personne n'ose le nettoyer.

ATTENTION : fichier d'exemple, volontairement vulnérable, ne sert qu'à
donner de la matière au scanner AegisLegacy. Ne jamais lancer tel quel.
"""

import pickle

import yaml


def load_legacy_config(path: str) -> dict:
    # yaml.load() sans Loader=SafeLoader peut exécuter du code arbitraire
    # si le fichier contient un tag !!python/object.
    with open(path) as f:
        return yaml.load(f)


def load_cached_session(path: str) -> object:
    # pickle.load() désérialise et exécute potentiellement du code si le
    # fichier a été modifié par quelqu'un d'autre que nous.
    with open(path, "rb") as f:
        return pickle.load(f)


def run_user_formula(formula: str, variables: dict) -> object:
    # Une "formule" tapée par l'utilisateur, évaluée telle quelle. Une
    # fonctionnalité "avancée" ajoutée en urgence pour un client, jamais
    # revue depuis.
    return eval(formula, {"__builtins__": {}}, variables)
