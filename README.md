# ArubaIO-MCP

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for **HPE Aruba Instant On**. It lets an MCP-capable AI client query your Instant On sites, devices, clients, alerts and networks through the Instant On cloud portal API.

All tools are **read-only**. The server cannot change your configuration.

> **Unofficial.** This project is not affiliated with or endorsed by HPE/Aruba. It uses the same web portal API as the Instant On web app. The API is undocumented and may change without notice. Endpoint knowledge is based on lwhitelock's Instant On PowerShell script.

## Tools

Every site tool takes a `site_identifier`, which can be the site name, a unique name prefix, or the site UUID.

| Tool | Description |
|------|-------------|
| `aruba_list_sites` | List all sites on the account |
| `aruba_get_site_details` | Details for one site |
| `aruba_get_site_summary` | Site inventory summary |
| `aruba_list_devices` | Access points and switches |
| `aruba_list_clients` | All connected clients |
| `aruba_list_wired_clients` | Wired clients only |
| `aruba_list_wireless_clients` | Wireless clients only |
| `aruba_list_alerts` | Active alerts |
| `aruba_get_alerts_summary` | Alert counts by severity |
| `aruba_get_application_usage` | Application usage statistics |
| `aruba_list_wireless_networks` | Wi-Fi networks (see security notes) |
| `aruba_list_wired_networks` | Wired networks / VLANs |
| `aruba_get_site_administration` | Site administration settings |
| `aruba_get_site_timezone` | Site timezone |
| `aruba_get_site_maintenance` | Maintenance window settings |

## Security notes

- `aruba_list_wireless_networks` returns Wi-Fi **pre-shared keys in plain text**. Treat anyone who can call this server as an administrator.
- Over HTTP the server **requires** a bearer token (`MCP_AUTH_TOKEN`) and refuses to start without one. Use a long random value, for example `openssl rand -hex 32`.
- Never commit your `.env` file. It is gitignored.
- Use an Instant On account with only the access you need.

## Requirements

- An HPE Aruba Instant On account (username and password) with access to your sites. MFA must not be required for the account used.
- Python 3.10 or newer (the Docker image uses 3.13), **or** Docker.
- Python packages: `fastmcp`, `httpx`, `python-dotenv` (see `requirements.txt`).

## Configuration

Copy `.env.example` to `.env` and fill it in:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ARUBA_USERNAME` | yes | | Instant On account email |
| `ARUBA_PASSWORD` | yes | | Instant On account password |
| `MCP_TRANSPORT` | no | `stdio` | `stdio` or an HTTP transport such as `streamable-http` |
| `MCP_AUTH_TOKEN` | for HTTP | | Bearer token clients must send |
| `MCP_HTTP_HOST` | no | `0.0.0.0` | Bind address for HTTP transports |
| `MCP_HTTP_PORT` | no | `8830` | Port for HTTP transports |

## Installation

### Option 1: Run locally (stdio)

```bash
git clone https://github.com/AndyAIT/ArubaIO-MCP.git
cd ArubaIO-MCP
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # then edit .env
python server.py
```

Example client configuration for a stdio MCP client:

```json
{
  "mcpServers": {
    "aruba-instant-on": {
      "command": "/path/to/ArubaIO-MCP/.venv/bin/python",
      "args": ["/path/to/ArubaIO-MCP/server.py"]
    }
  }
}
```

### Option 2: Docker (HTTP)

```bash
git clone https://github.com/AndyAIT/ArubaIO-MCP.git
cd ArubaIO-MCP
cp .env.example .env             # set ARUBA_USERNAME, ARUBA_PASSWORD, MCP_AUTH_TOKEN
docker compose up -d --build
```

The container serves streamable HTTP at `http://127.0.0.1:8830/mcp`. The bundled `docker-compose.yml` publishes the port on the host's loopback interface only. Clients must send `Authorization: Bearer <MCP_AUTH_TOKEN>`.

### Adding to an existing compose stack

To run it beside other services, for example a `cloudflared` tunnel, add a service like this:

```yaml
  aruba-mcp:
    build: ./ArubaIO-MCP
    container_name: aruba-mcp
    restart: unless-stopped
    environment:
      MCP_TRANSPORT: streamable-http
      MCP_HTTP_HOST: 0.0.0.0
      MCP_HTTP_PORT: 8830
      MCP_AUTH_TOKEN: ${ARUBA_MCP_AUTH_TOKEN}
      ARUBA_USERNAME: ${ARUBA_USERNAME}
      ARUBA_PASSWORD: ${ARUBA_PASSWORD}
    # No ports published: the tunnel reaches it over the compose network.
```

Point the tunnel's public hostname at `http://aruba-mcp:8830`. Keep the bearer token enabled whenever the service is reachable from the internet.

## Verifying it works

```bash
# Expect 401 without a token
curl -i -X POST http://127.0.0.1:8830/mcp
```

## How it works

The client signs in through Instant On SSO, completes an OAuth PKCE flow against the portal, and calls `https://nb.portal.arubainstanton.com`. Access tokens refresh automatically and the site list is cached for 60 seconds.

## Project layout

| File | Purpose |
|------|---------|
| `server.py` | FastMCP server, tool definitions, transport and auth |
| `aruba_client.py` | Instant On API client |
| `Dockerfile`, `docker-compose.yml` | Container build and run configuration |
| `requirements.txt` | Python dependencies |
