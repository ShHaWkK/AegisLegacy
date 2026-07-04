# Modernization Rules

Not implemented yet in this iteration. See [../../ROADMAP.md](../../ROADMAP.md).

Will hold heuristic rules feeding the "Modernization Advisor" (e.g. "Perl
CGI script → candidate for a FastAPI endpoint", "oversized module → extract
business logic behind an interface"), reusing the same `RuleDefinition`
loader with an extended `advice` field.
