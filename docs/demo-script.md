# Script de démo — AegisLegacy

Ce document sert à préparer une démo live (entretien, portfolio) en 3-5
minutes. Toutes les commandes sont copiables telles quelles depuis la
racine du repo.

## 0. Avant de commencer

Installer une fois (voir [../README.md](../README.md) pour le détail) :

```bash
python -m venv .venv
.venv/Scripts/activate          # ou : source .venv/bin/activate
pip install -e "backend[dev,api]" -e "cli[dev]"
```

## 1. Le CLI — la façon la plus rapide de montrer le produit

```bash
aegis scan demo-legacy-app
```

Ce que ça montre : une table de findings colorée par sévérité, un score
de sécurité, et un code de sortie non-zéro (2) puisqu'il y a des findings
critiques — utile à mentionner si on parle CI/CD ("le scan peut faire
échouer un pipeline").

Deux commandes complémentaires, si on a le temps :

```bash
aegis rules list      # montre les 8 règles chargées, avec leur sévérité
aegis doctor          # vérifie que l'environnement est sain
```

## 2. Le backend API — pour montrer que ce n'est pas qu'un script

```bash
uvicorn app.main:app --app-dir backend --reload
```

Dans un autre terminal :

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/api/v1/scans \
  -H "Content-Type: application/json" -H "X-API-Key: changeme-local-dev-key" \
  -d '{"target_path": "demo-legacy-app"}'
```

La réponse donne un `id` de scan. On peut ensuite montrer :

```bash
curl http://127.0.0.1:8000/api/v1/scans/1/findings
curl http://127.0.0.1:8000/api/v1/scans/1/score
curl http://127.0.0.1:8000/api/v1/scans
```

Et la doc interactive, dans un navigateur : `http://127.0.0.1:8000/docs`
(générée automatiquement par FastAPI — bon réflexe à montrer si on parle
d'API design).

## 3. L'agent Perl — pour montrer le côté "legacy" du projet

```bash
perl agent-perl/bin/aegis-agent.pl --path demo-legacy-app
```

Point à mentionner : cet agent ne dépend d'aucun module externe (que du
cœur de Perl), donc il tourne sur une machine qui n'a même pas Python.
C'est volontairement un sous-ensemble plus léger de règles que le moteur
Python — la source de vérité pour la détection reste `rules/*.yaml`.

## 4. Ce que la démo doit faire ressortir

- **Trois façons d'accéder au même moteur de détection** (CLI, API,
  agent Perl) sans dupliquer la logique de scan (`app.rules.engine`).
- **Un score explicable** : chaque point perdu correspond à un finding
  précis, pas une boîte noire.
- **Du code legacy réel scanné** (`demo-legacy-app/`) : `system()` avec
  entrée utilisateur, `subprocess(shell=True)`, `eval()`, désérialisation
  dangereuse, secrets en dur — les classiques d'un audit de sécurité.

## Si on te demande "et si je scanne mon propre projet ?"

```bash
aegis scan /chemin/vers/un/vrai/projet
```

Ça marche sur n'importe quel dossier Perl/Python — la démo n'est qu'un
fixture, pas une limite du produit.
