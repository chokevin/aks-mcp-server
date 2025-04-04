import httpx
from mcp.server.fastmcp import FastMCP
from typing import Any
import subprocess
import json


# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


# Initialize Weather Tools
def init_weather_tools(mcp: FastMCP):
    """Initialize tools for the FastMCP server."""

    @mcp.tool()
    async def get_aks_clusters(state: str) -> str:
        """Get Azure AKS clusters using the Azure CLI.

        Args:
            state: Filter parameter (can be resource group or any filter criteria)
        """
        try:
            # Run the az aks list command
            cmd = ["az", "aks", "list"]

            # Add resource group filter if state is provided and looks like a resource group name
            if state and state.strip():
                cmd.extend(["--resource-group", state])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse the JSON output
            clusters = json.loads(result.stdout)

            if not clusters:
                return "No AKS clusters found."

            # Format the results nicely
            formatted_output = []
            for cluster in clusters:
                formatted_output.append(f"Name: {cluster.get('name')}")
                formatted_output.append(
                    f"Resource Group: {cluster.get('resourceGroup')}"
                )
                formatted_output.append(f"Location: {cluster.get('location')}")
                formatted_output.append(
                    f"Kubernetes Version: {cluster.get('kubernetesVersion')}"
                )
                formatted_output.append(f"Status: {cluster.get('provisioningState')}")
                formatted_output.append("---")

            return "\n".join(formatted_output)
        except subprocess.CalledProcessError as e:
            # Handle errors like when az CLI isn't installed or authentication failures
            return f"Error executing Azure CLI command: {e.stderr}"
        except json.JSONDecodeError:
            return "Error parsing Azure CLI output"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_alerts(state: str) -> str:
        """Get weather alerts for a US state.

        Args:
            state: Two-letter US state code (e.g. CA, NY)
        """
        url = f"{NWS_API_BASE}/alerts/active/area/{state}"
        data = await make_nws_request(url)

        if not data or "features" not in data:
            return "Unable to fetch alerts or no alerts found."

        if not data["features"]:
            return "No active alerts for this state."

        alerts = [format_alert(feature) for feature in data["features"]]
        return "\n---\n".join(alerts)

    @mcp.tool()
    async def get_forecast(latitude: float, longitude: float) -> str:
        """Get weather forecast for a location.

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
        """
        # First get the forecast grid endpoint
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await make_nws_request(points_url)

        if not points_data:
            return "Unable to fetch forecast data for this location."

        # Get the forecast URL from the points response
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_request(forecast_url)

        if not forecast_data:
            return "Unable to fetch detailed forecast."

        # Format the periods into a readable forecast
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
    {period['name']}:
    Temperature: {period['temperature']}°{period['temperatureUnit']}
    Wind: {period['windSpeed']} {period['windDirection']}
    Forecast: {period['detailedForecast']}
    """
            forecasts.append(forecast)

        return "\n---\n".join(forecasts)
