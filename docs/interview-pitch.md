# Pitch entretien — AegisLegacy

## En 30 secondes

> "AegisLegacy, c'est un outil de scan de sécurité pour du code legacy
> Perl et Python — je l'ai construit pour démontrer une approche senior :
> architecture propre (domaine séparé de l'infra), un moteur de règles
> testé à 100%, une API FastAPI avec persistance, un CLI, et même un
> agent Perl autonome qui ne dépend d'aucune librairie externe. Trois
> façons différentes de scanner le même code, sans dupliquer la logique
> de détection."

## En 2 minutes

> "Le projet part d'un constat simple : dans beaucoup d'équipes, il y a
> du code Perl ou Python ancien que personne n'ose toucher — des
> `system()` avec des entrées utilisateur, du `eval()`, des secrets en
> dur. AegisLegacy scanne ce genre de code et sort un score de sécurité
> avec le détail des findings.
>
> Techniquement, j'ai construit ça dans un ordre précis, en dépendance :
> d'abord le moteur de règles (Python, régler YAML, findings normalisés,
> scoring) parce que tout le reste en dépend. Ensuite le CLI, qui valide
> que le moteur marche de bout en bout sans avoir besoin de base de
> données. Ensuite le backend FastAPI, qui ajoute la persistance SQLite
> et une vraie API REST. Et enfin un agent Perl indépendant, qui prouve
> que la détection ne dépend pas d'un seul langage.
>
> Ce qui me semble le plus intéressant à montrer : chaque module est
> testé (plus de 100 tests au total), lint et typé strictement (mypy
> --strict), et je documente explicitement ce qui n'est PAS fait plutôt
> que de faire semblant — par exemple, il n'y a pas encore de génération
> de rapport HTML, et je le dis clairement dans le ROADMAP au lieu de
> laisser un endpoint qui ne marche qu'à moitié."

## Sur l'architecture

- Séparation claire : `domain/` (modèles purs, sans I/O) → `rules/`
  (chargement + matching) → `services/` (orchestration + scoring) →
  `api/` / `repositories/` (les seules couches qui touchent le réseau ou
  la base de données).
- Le CLI et le backend API partagent le même exécuteur de scan
  (`app.services.scan_runner.execute_scan`) — pas de logique dupliquée
  entre les deux, découvert et corrigé pendant une revue de code.
- Une chose que je peux assumer si on me pousse dessus : oui, il y a des
  choix de scope volontaires (pas de Celery/Redis, scans synchrones,
  SQLite plutôt que Postgres) — je peux expliquer pourquoi et comment je
  les ferais évoluer.

## Sur la sécurité

- Le scanner détecte 8 patterns : injection de commande (Perl et
  Python), `eval`/`exec` non sécurisés, désérialisation dangereuse
  (`pickle`, `yaml.load`), secrets en dur (génériques + format clé AWS).
- Le scoring est explicable : score de départ 100, pénalité fixe par
  sévérité (critique -20, haute -10, moyenne -5, basse -2, info -0.5),
  jamais de boîte noire.
- L'authentification de l'API est volontairement simple (clé API en
  header, comparaison à temps constant) — proportionné à ce que fait
  l'API aujourd'hui, pas une usine à gaz OAuth pour un outil interne.
- Le fixture de démo (`demo-legacy-app/`) ne contient que des secrets
  inventés, jamais de vraies clés.

## Sur le choix Python

- Python 3.12, typage complet, Pydantic v2 pour toute donnée qui traverse
  une frontière (YAML, JSON, HTTP).
- FastAPI + SQLModel pour l'API — choix pragmatique pour aller vite tout
  en gardant du typage de bout en bout.
- Typer + Rich pour le CLI — sortie terminal lisible sans réinventer une
  lib d'affichage.

## Sur le choix Perl

- L'agent Perl ne dépend que du cœur du langage (`File::Find`,
  `Digest::SHA`, `JSON::PP`, `HTTP::Tiny`, `Getopt::Long`) — il tourne
  sur n'importe quelle install Perl, même minimale.
- Volontairement plus léger que le moteur Python (4 règles codées en dur
  contre 8 en YAML) : ce n'est pas une réimplémentation complète, c'est
  un scanner autonome pour un contexte où Python n'est pas disponible.
- Anecdote utile en entretien : en le testant en conditions réelles
  (pas juste avec les tests unitaires), j'ai trouvé un vrai bug —
  `File::Find` refusait un chemin relatif sur l'install Perl utilisée. Les
  tests unitaires ne l'avaient pas vu parce qu'ils passaient tous par des
  chemins absolus (`File::Temp::tempdir`). Corrigé en résolvant le
  chemin avec `Cwd::abs_path`, avec un test de non-régression ajouté
  après coup. Bon exemple concret de "les tests unitaires ne remplacent
  pas de faire tourner le vrai truc".

## Questions probables en entretien

**"Pourquoi pas juste utiliser bandit/semgrep existants ?"**
> Le projet n'a pas vocation à remplacer ces outils — c'est un exercice
> volontaire pour démontrer la construction d'un moteur de règles, d'une
> API et d'un CLI de A à Z, avec les compromis qui vont avec (regex vs
> AST, documenté explicitement dans le ROADMAP).

**"Qu'est-ce qui manque pour que ce soit production-ready ?"**
> Une queue de tâches (Celery/RQ) pour les gros scans, des migrations
> Alembic plutôt que `create_all`, un cache sur le chargement des règles,
> et un vrai système de comptes plutôt qu'une clé API unique. Tout est
> listé dans `ROADMAP.md`.

**"Comment tu as vérifié que ça marche vraiment, pas juste les tests ?"**
> À chaque module, en plus des tests automatisés, je l'ai lancé pour de
> vrai contre un cas concret — CLI contre du code vulnérable, serveur
> API démarré et interrogé en HTTP réel, agent Perl exécuté en ligne de
> commande. C'est comme ça que j'ai trouvé le bug `File::Find` mentionné
> plus haut, que les tests seuls n'auraient pas vu.
