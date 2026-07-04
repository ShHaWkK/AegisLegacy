# Demo Legacy App

Not implemented yet in this iteration. See [../ROADMAP.md](../ROADMAP.md).

This directory will contain a deliberately vulnerable, **local-only,
educational** legacy application used to exercise the rules engine:
a Perl CGI script, a Perl module using `system()`, a Python script using
`subprocess(..., shell=True)`, a `.env` with a fake secret, and a
misconfigured config file. All vulnerabilities are inert fixtures for
detection and reporting demos — no offensive tooling, no real secrets, no
exploitation code.
