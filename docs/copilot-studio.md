# Using ArubaIO-MCP as a Copilot Studio agent tool

Copilot Studio can call this server as an MCP tool. It supports the **Streamable** transport only (SSE is no longer supported), which is what this server uses over HTTP.

## Prerequisites

- The server is running over HTTP and reachable from the internet over **HTTPS**, for example through a Cloudflare tunnel: `https://your-host.example.com/mcp`.
- You know the `MCP_AUTH_TOKEN` value the server was started with.
- A Copilot Studio agent you can edit.

Check the endpoint first. An unauthenticated request should return `401`:

```bash
curl -i -X POST https://your-host.example.com/mcp
```

## Add the server to your agent

1. Open your agent in [Copilot Studio](https://copilotstudio.microsoft.com) and go to the **Tools** page.
2. Select **Add a tool**, then **New tool**.
3. Under **Create new**, choose **Model Context Protocol**.
4. Fill in the wizard:

   | Field | Value |
   |-------|-------|
   | Server name | `Aruba Instant On` |
   | Server description | See below |
   | Server URL | `https://your-host.example.com/mcp` |
   | Authentication | **API key** |
   | Type | **Header** |
   | Header name | `Authorization` |

5. Select **Create**.
6. On the **Add tool** dialog, choose **Create a new connection**. When prompted for the API key, enter `Bearer <MCP_AUTH_TOKEN>`, including the word `Bearer` and a space. Copilot Studio sends the value as-is in the header, and this server expects `Authorization: Bearer <token>`.
7. Select **Create**, then add the tool to the agent.

Suggested server description (the agent uses it to decide when to call the tools):

> Read-only access to HPE Aruba Instant On networks. Lists sites, devices, connected wired and wireless clients, alerts, application usage, Wi-Fi and wired networks, and site settings. Use it to answer questions about the health and status of customer sites.

OAuth 2.0 is not needed. This server uses a static bearer token.

## Configure the agent

1. Open the agent's **Overview** and add instructions, for example:

   > You help IT staff check Aruba Instant On sites. Use the Aruba Instant On tools to answer questions about sites, devices, clients and alerts. Site names can be partial. If a name matches more than one site, ask which one is meant. Never guess data; say when a tool returns nothing.

2. On the **Tools** page, open the Aruba tool and review the 15 tools it lists. Their descriptions come from the server.
3. Make sure generative orchestration is on, so the agent chooses tools by itself.

## Test it

In the test pane, try:

- "List all Aruba sites."
- "How many wireless clients are on Fabrikam?"
- "Any active alerts at Contoso IT?"

If a call fails, check the tool details in the test pane for the error.

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| Connection fails with 401 | The key is wrong or missing `Bearer `. Recreate the connection. |
| Cannot reach the server | The URL must be HTTPS and end in `/mcp`, and the tunnel must be up. |
| Wi-Fi keys show `***REDACTED***` | Intended. Set `MCP_REDACT_SECRETS=false` on the server to return them. |
| Tools missing after a server update | Remove and re-add the tool, or refresh the tool list on the Tools page. |

## Security

- Anyone who can edit the agent or use the connection can call the tools. Share the agent only with trusted users.
- Keep `MCP_REDACT_SECRETS` at its default (`true`) unless you need the keys. Returning them in plain text puts them into chat history.
- Rotate `MCP_AUTH_TOKEN` if it is ever exposed, then update the connection in Copilot Studio.

Reference: [Connect your agent to an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent).
