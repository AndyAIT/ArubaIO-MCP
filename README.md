# ArubaIO-MCP

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for **HPE Aruba Instant On**. It lets an MCP-capable AI client query your Instant On sites, devices, clients, alerts and networks through the Instant On cloud portal API.

All tools are **read-only**. The server cannot change your configuration.

> **Unofficial.** This project is not affiliated with or endorsed by HPE/Aruba. It uses the same web portal API as the Instant On web app. The API is undocumented and may change without notice.

## Credits

This project would not exist without the work of **[lwhitelock](https://github.com/lwhitelock)** (Luke Whitelock), whose Aruba Instant On PowerShell script documented the login flow and the API endpoints used here. Thank you for making your work available, and for allowing it to be used as the reference for this project.

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

- `aruba_list_wireless_networks` **redacts Wi-Fi pre-shared keys by default**. Set `MCP_REDACT_SECRETS=false` to return them in plain text; if you do, treat anyone who can call the server as an administrator.
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
| `MCP_REDACT_SECRETS` | no | `true` | Redact Wi-Fi pre-shared keys in tool output |

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

To use the server from a Microsoft Copilot Studio agent, see [docs/copilot-studio.md](docs/copilot-studio.md).

## Verifying it works

```bash
# Expect 401 without a token
curl -i -X POST http://127.0.0.1:8830/mcp
```

Or run the whole handshake yourself with an authenticated client, for example with `fastmcp`:

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    transport = StreamableHttpTransport("http://127.0.0.1:8830/mcp", auth="<MCP_AUTH_TOKEN>")
    async with Client(transport) as client:
        print(len(await client.list_tools()), "tools")
        print((await client.call_tool("aruba_list_sites", {})).content[0].text)

asyncio.run(main())
```

## Known limitations

- The Instant On API is unofficial and undocumented, so it can change without notice.
- Accounts that require MFA are not supported.
- A wired client summary endpoint exists in the reference script but returns 404 on tested sites, so it is not exposed. Wired clients come from the client list, filtered by type.
- Tested against one account with three sites; other regions or device mixes are unverified.
- All tools are read-only. There is no way to change settings.

## Development

```bash
pip install -r requirements.txt pytest
pytest
```

The tests use mocked API responses and need no Aruba credentials. CI runs them and builds the Docker image on each push.

## How it works

The client signs in through Instant On SSO, completes an OAuth PKCE flow against the portal, and calls `https://nb.portal.arubainstanton.com`. Access tokens refresh automatically and the site list is cached for 60 seconds.

## Project layout

| File | Purpose |
|------|---------|
| `server.py` | FastMCP server, tool definitions, transport and auth |
| `aruba_client.py` | Instant On API client |
| `Dockerfile`, `docker-compose.yml` | Container build and run configuration |
| `requirements.txt` | Python dependencies |
| `tests/` | Unit tests (mocked) |

## License

MIT. See [LICENSE](LICENSE). Changes are listed in [CHANGELOG.md](CHANGELOG.md); report security issues as described in [SECURITY.md](SECURITY.md).
