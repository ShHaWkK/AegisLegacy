# AegisLegacy Perl Agent

Not implemented yet in this iteration. See [../ROADMAP.md](../ROADMAP.md).

Planned: a standalone Perl 5 agent (`bin/aegis-agent.pl` + `lib/Aegis/*.pm`,
tested with `Test::More`) that walks a legacy tree, collects file metadata
and hashes, applies lightweight pattern checks, and emits JSON compatible
with the `Finding` schema used by the Python backend — either to a local
file or by POSTing to the backend API.
