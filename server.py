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
def aruba_get_site_details(site_identifier: str) -> dict:
    """Get detailed information about an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_details(site_identifier)


@mcp.tool()
def aruba_list_devices(site_identifier: str) -> list:
    """List switches and access points at an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.list_devices(site_identifier)


@mcp.tool()
def aruba_list_clients(site_identifier: str) -> list:
    """List all wired and wireless clients at an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.list_clients(site_identifier)


@mcp.tool()
def aruba_list_wired_clients(site_identifier: str) -> list:
    """List wired clients connected to an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.list_clients(site_identifier, client_type="wired")


@mcp.tool()
def aruba_list_wireless_clients(site_identifier: str) -> list:
    """List wireless clients connected to an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.list_clients(site_identifier, client_type="wireless")


@mcp.tool()
def aruba_get_site_summary(site_identifier: str) -> dict:
    """Get the landing page summary for an Aruba Instant On site: client and network counts, throughput and 24h data usage. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "landingPage")


@mcp.tool()
def aruba_get_site_administration(site_identifier: str) -> dict:
    """Get administration details for an Aruba Instant On site, including admin accounts. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "administration")


@mcp.tool()
def aruba_get_site_timezone(site_identifier: str) -> dict:
    """Get the timezone and current local time of an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "timezone")


@mcp.tool()
def aruba_get_site_maintenance(site_identifier: str) -> dict:
    """Get the firmware version, update state and maintenance window of an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "maintenance")


@mcp.tool()
def aruba_list_alerts(site_identifier: str) -> list:
    """List alerts for an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "alerts", list_result=True)


@mcp.tool()
def aruba_get_alerts_summary(site_identifier: str) -> dict:
    """Get counts of active info, minor and major alerts for an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "alertsSummary")


@mcp.tool()
def aruba_get_application_usage(site_identifier: str) -> list:
    """List 24-hour data usage by application category and SSID for an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "applicationCategoryUsage", list_result=True)


@mcp.tool()
def aruba_list_wireless_networks(site_identifier: str) -> list:
    """List wireless networks (SSIDs) at an Aruba Instant On site, including security settings and pre-shared keys. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "networksSummary", list_result=True)


@mcp.tool()
def aruba_list_wired_networks(site_identifier: str) -> list:
    """List wired networks at an Aruba Instant On site. Site identifier can be a UUID or name."""
    return client.get_site_resource(site_identifier, "wiredNetworks", list_result=True)


if __name__ == "__main__":
    mcp.run()
