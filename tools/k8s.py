from mcp.server.fastmcp import FastMCP
from typing import Any
import subprocess
import json
import logging

logger = logging.getLogger("aks-mcp.tools.k8s")


def init_k8s_tools(mcp: FastMCP):
    """Initialize tools for the FastMCP server."""

    @mcp.tool()
    async def analyze_k8s_cluster(
        explain: bool = True,
        filter: str = None,
        namespace: str = None,
        with_doc: bool = False,
        output_format: str = "text",
        anonymize: bool = False,
        backend: str = None,
    ) -> str:
        """Analyze Kubernetes cluster issues using k8sgpt.

        Args:
            explain: Whether to provide detailed AI explanations of issues (default: True)
            filter: Filter analysis to a specific resource type (e.g., Pod, Service, Deployment)
            namespace: Filter analysis to a specific namespace
            with_doc: Include official Kubernetes documentation references (default: False)
            output_format: Output format (text, json, yaml) (default: text)
            anonymize: Anonymize resource names in output (default: False)
            backend: Specify which AI backend to use (default: system default)
        """
        try:
            # Build the k8sgpt analyze command
            cmd = ["k8sgpt", "analyze"]

            # Add optional parameters
            if explain:
                cmd.append("--explain")

            if filter:
                cmd.extend(["--filter", filter])

            if namespace:
                cmd.extend(["--namespace", namespace])

            if with_doc:
                cmd.append("--with-doc")

            if output_format and output_format.lower() in ["text", "json", "yaml"]:
                cmd.extend(["--output", output_format.lower()])

            if anonymize:
                cmd.append("--anonymize")

            if backend:
                cmd.extend(["--backend", backend])

            # Execute the command
            logger.info(f"Executing k8sgpt command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Handle different output formats
            if output_format and output_format.lower() == "json":
                try:
                    # If it's JSON, we can parse it for better readability
                    analysis = json.loads(result.stdout)
                    return json.dumps(analysis, indent=2)
                except json.JSONDecodeError:
                    # If parsing fails, return raw output
                    return result.stdout
            else:
                # Return raw text output
                return (
                    result.stdout
                    if result.stdout
                    else "No issues found in the cluster."
                )

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout
            if "k8sgpt: command not found" in error_msg:
                return "Error: k8sgpt is not installed. Please install it first with 'brew install k8sgpt' or follow the installation guide at https://github.com/k8sgpt-ai/k8sgpt"
            elif "authentication required" in error_msg or "auth" in error_msg:
                return "Error: k8sgpt requires authentication setup. Please run 'k8sgpt auth add' to configure your AI provider."
            return f"Error executing k8sgpt: {error_msg}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def k8sgpt_configure_auth(
        provider: str = "azureopenai", api_key: str = None
    ) -> str:
        """Configure k8sgpt authentication for AI provider.

        Args:
            provider: AI provider to configure (default: azureopenai)
            api_key: API key for the provider (if not provided, will prompt in terminal)
        """
        try:
            # First check if k8sgpt is installed
            try:
                subprocess.run(["k8sgpt", "--version"], capture_output=True, check=True)
            except FileNotFoundError:
                return "Error: k8sgpt is not installed. Please install it first with 'brew install k8sgpt' or follow the installation guide at https://github.com/k8sgpt-ai/k8sgpt"

            # Configure auth
            if api_key:
                # Add auth with provided API key
                cmd = ["k8sgpt", "auth", "add", "-p", provider, "--password", api_key]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return f"Successfully configured {provider} authentication for k8sgpt."
            else:
                # Return instructions since we can't request interactive input
                return (
                    f"To configure {provider} authentication for k8sgpt, please run the "
                    f"following command in your terminal:\n\n"
                    f"k8sgpt auth add -p {provider}\n\n"
                    f"You will be prompted to enter your API key."
                )

        except subprocess.CalledProcessError as e:
            return f"Error configuring k8sgpt authentication: {e.stderr if e.stderr else e.stdout}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def k8sgpt_list_filters() -> str:
        """List available k8sgpt analysis filters.

        Args:
            None
        """
        try:
            cmd = ["k8sgpt", "filters"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError as e:
            if "k8sgpt: command not found" in e.stderr:
                return "Error: k8sgpt is not installed. Please install it first with 'brew install k8sgpt' or follow the installation guide at https://github.com/k8sgpt-ai/k8sgpt"
            return f"Error listing k8sgpt filters: {e.stderr if e.stderr else e.stdout}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
