# Agent Perl AegisLegacy

Un agent Perl 5 autonome, sans dépendance externe à installer : tous les
modules utilisés (`File::Find`, `Digest::SHA`, `JSON::PP`, `HTTP::Tiny`,
`Getopt::Long`, `Test::More`) font partie du cœur de Perl.

## Pourquoi un agent séparé du moteur Python ?

Ce n'est volontairement **pas** une réimplémentation complète du moteur de
règles Python (`backend/app/rules`). L'agent Perl :

- parcourt un dossier legacy et calcule les métadonnées de chaque fichier
  pertinent (taille, date, hash SHA-256) — `Aegis::Collector` ;
- applique un petit jeu de règles à haute valeur, codées en dur (pas de
  YAML, donc pas de dépendance supplémentaire) — `Aegis::Scanner` ;
- assemble un rapport JSON et l'écrit sur disque ou l'envoie en HTTP —
  `Aegis::Reporter`.

La source de vérité pour la détection exhaustive reste le moteur Python
(`rules/*.yaml`). L'agent Perl est utile pour scanner une machine où
Python n'est pas disponible, ou comme collecteur léger indépendant.

## Utilisation

```bash
# Affiche le rapport JSON sur STDOUT
perl bin/aegis-agent.pl --path ./demo-legacy-app

# Écrit le rapport dans un fichier
perl bin/aegis-agent.pl --path ./demo-legacy-app --output scan.json

# Envoie le rapport en POST vers une URL
perl bin/aegis-agent.pl --path ./demo-legacy-app --api http://localhost:8000/api/v1/scans
```

Codes de sortie : `0` si aucun finding critique, `2` si au moins un
finding critique, `1` en cas d'erreur (chemin invalide, échec d'écriture
ou d'envoi, usage incorrect).

Remarque : `--api` envoie tel quel le rapport JSON généré localement (avec
ses propres findings) vers l'URL donnée, via un simple POST HTTP. Le
backend actuel (`POST /api/v1/scans`) attend un `{"target_path": "..."}`
et exécute lui-même le scan Python — il n'y a pas encore d'endpoint dédié
à l'ingestion de findings pré-calculés par l'agent Perl (voir
`../ROADMAP.md`).

## Règles détectées

| ID | Langage | Sévérité | Catégorie |
|---|---|---|---|
| AGENT-CMD-001 | perl | critical | command-injection |
| AGENT-EVAL-001 | perl | high | unsafe-eval |
| AGENT-SUBPROC-001 | python | critical | command-injection |
| AGENT-SECRET-001 | any | critical | hardcoded-secret |

## Tests

```bash
cd agent-perl
prove -l t/
```

## Structure

```text
agent-perl/
├── bin/aegis-agent.pl       point d'entrée CLI
├── lib/Aegis/
│   ├── Utils.pm             hash, lecture fichier, chemin relatif
│   ├── Collector.pm         parcours de l'arbre + métadonnées
│   ├── Scanner.pm           détection de patterns
│   └── Reporter.pm          assemblage du rapport + export JSON/HTTP
├── t/                       tests Test::More
└── cpanfile
```
