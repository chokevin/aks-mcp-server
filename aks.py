from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import uvicorn
import tools
import sys


# Initialize FastMCP server
mcp = FastMCP("aks-mcp")

tools.init_tools(mcp)

if __name__ == "__main__":
    # Initialize and run the server
    try:
        mcp.run()
    except Exception as e:
        print(f"Server shutdown with error: {e}", file=sys.stderr)
    finally:
        print("Server has been shutdown", file=sys.stderr)
