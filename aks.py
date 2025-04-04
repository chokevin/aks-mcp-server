from typing import Any
import sys
from mcp.server.fastmcp import FastMCP

import tools.toolcase as toolcase


# Initialize FastMCP server
mcp = FastMCP("aks-mcp")

# Initialize tools directly
toolcase.init_tools(mcp)

if __name__ == "__main__":
    # Initialize and run the server
    try:
        mcp.run()
    except Exception as e:
        print(f"Server shutdown with error: {e}", file=sys.stderr)
    finally:
        print("Server has been shutdown", file=sys.stderr)
