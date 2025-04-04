from mcp.server.fastmcp import FastMCP
from typing import Any
import logging

from tools.aks import init_aks_tools
from tools.weather import init_weather_tools
from tools.k8s import init_k8s_tools

logger = logging.getLogger("aks-mcp.toolcase")


# Initialize FastMCP server
def init_tools(mcp: FastMCP):
    init_aks_tools(mcp)
    init_weather_tools(mcp)
    init_k8s_tools(mcp)
