# Demo Legacy App

C'est le "patient" sur lequel on teste AegisLegacy : une petite appli
fictive, volontairement pleine de mauvaises pratiques classiques du code
legacy. Rien de tout ça ne tourne réellement — pas de serveur, pas
d'exécution, juste des fichiers texte à scanner.

**Aucun vrai secret, aucun code offensif réutilisable.** Les mots de
passe et clés API sont inventés (`hunter2super`, une clé au format AWS
mais bidon) — jamais de vraies clés qui auraient pu fuiter ailleurs.

## Ce qu'il y a dedans

| Fichier | Ce qu'il illustre | Règle(s) déclenchée(s) |
|---|---|---|
| `perl-cgi/upload.cgi` | `system()` avec un nom de fichier venant d'un formulaire, `open` à 2 arguments | `PERL-CMD-001`, `PERL-OPEN-001` |
| `perl-cgi/plugin_loader.pl` | `eval` d'une chaîne construite à partir d'une entrée utilisateur | `PERL-EVAL-001` |
| `python-scripts/backup.py` | `subprocess.run(..., shell=True)` avec une chaîne interpolée | `PY-SUBPROC-001` |
| `python-scripts/legacy_loader.py` | `yaml.load()` sans `SafeLoader`, `pickle.load()`, `eval()` | `PY-DESERIAL-001`, `PY-EVAL-001` |
| `.env` | Mot de passe et token en dur | `SECRET-GENERIC-001` |
| `config/app.conf` | Mot de passe + clé au format AWS en dur | `SECRET-GENERIC-001`, `SECRET-AWS-001` |

## Comment le scanner

Depuis la racine du repo, avec le CLI installé (voir [../cli/README.md](../cli/README.md)) :

```bash
aegis scan demo-legacy-app
```

Ou avec l'agent Perl, sans rien installer :

```bash
perl agent-perl/bin/aegis-agent.pl --path demo-legacy-app
```

Ou via l'API (le serveur doit tourner, voir [../README.md](../README.md)) :

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scans \
  -H "Content-Type: application/json" -H "X-API-Key: changeme-local-dev-key" \
  -d '{"target_path": "demo-legacy-app"}'
```

Les trois donnent le même résultat de fond : un score très bas (autour de
5-10/100, classification "Critical"), avec la majorité des findings en
sévérité critique.
