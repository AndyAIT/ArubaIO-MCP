from fastmcp import FastMCP
from aruba_client import ArubaInstantOnClient

# Initialize FastMCP
mcp = FastMCP("Aruba Instant On MCP")

# Initialize Aruba API client
client = ArubaInstantOnClient()


@mcp.tool()
def aruba_list_sites() -> list:
    """List all Aruba Instant On sites."""
    return client.list_sites()


@mcp.tool()
def aruba_get_site_details(site_id: str) -> dict:
    """Get detailed information about an Aruba Instant On site."""
    return client.get_site_details(site_id)


@mcp.tool()
def aruba_list_devices(site_id: str) -> list:
    """List switches and access points at an Aruba Instant On site."""
    return client.list_devices(site_id)


@mcp.tool()
def aruba_list_clients(site_id: str) -> dict:
    """List all wired and wireless clients at an Aruba Instant On site."""
    return client.list_clients(site_id)


@mcp.tool()
def aruba_list_wired_clients(site_id: str) -> list:
    """List wired clients connected to an Aruba Instant On site."""
    result = client.list_clients(site_id)

    return [
        c for c in result.get("elements", [])
        if c.get("clientType") == "wired"
    ]


@mcp.tool()
def aruba_list_wireless_clients(site_id: str) -> list:
    """List wireless clients connected to an Aruba Instant On site."""
    result = client.list_clients(site_id)

    return [
        c for c in result.get("elements", [])
        if c.get("clientType") == "wireless"
    ]


if __name__ == "__main__":
    mcp.run()