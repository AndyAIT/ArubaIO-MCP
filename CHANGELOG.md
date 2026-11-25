# Changelog

## 0.1.0

Initial release.

- 15 read-only tools for Aruba Instant On sites, devices, clients, alerts, usage and networks.
- Site lookup by name, unique name prefix or UUID, with a 60 second site cache.
- Automatic token refresh with a single retry on 401.
- stdio and streamable-HTTP transports; bearer-token auth is mandatory over HTTP.
- Wi-Fi pre-shared keys are redacted by default (`MCP_REDACT_SECRETS=false` to disable).
- Docker image and compose configuration.
