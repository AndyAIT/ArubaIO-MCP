# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's "Report a vulnerability" option on the repository's Security tab, rather than opening a public issue. Do not include real credentials, tokens or Wi-Fi keys in reports.

## Notes for operators

- Over HTTP, always set a long random `MCP_AUTH_TOKEN` (for example `openssl rand -hex 32`) and keep the container off public ports; expose it only through a trusted tunnel or reverse proxy.
- The server holds your Aruba Instant On credentials. Use a dedicated account with the least access you need, and never commit `.env`.
- Wi-Fi pre-shared keys are redacted by default. Setting `MCP_REDACT_SECRETS=false` returns them in plain text to anyone holding the token.
