from mcp.server.fastmcp import FastMCP
from typing import Any
import subprocess
import json
import logging

logger = logging.getLogger("aks-mcp.tools")


def init_aks_tools(mcp: FastMCP):
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
    async def show_aks_cluster(cluster_name: str, resource_group_name: str) -> str:
        """Show details of a specific AKS cluster using the Azure CLI.

        Args:
            cluster_name: Name of the AKS cluster
            resource_group_name: Name of the resource group
        """
        try:
            # Run the az aks show command
            cmd = [
                "az",
                "aks",
                "show",
                "--name",
                cluster_name,
                "--resource-group",
                resource_group_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse the JSON output
            cluster_details = json.loads(result.stdout)

            if not cluster_details:
                return "No AKS cluster found."

            # Format the results nicely
            formatted_output = []
            for key, value in cluster_details.items():
                formatted_output.append(f"{key}: {value}")
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
    async def set_aks_credentials(cluster_name: str, resource_group_name: str) -> str:
        """Set AKS credentials using the Azure CLI.

        Args:
            cluster_name: Name of the AKS cluster
            resource_group_name: Name of the resource group
        """
        try:
            # Run the az aks get-credentials command
            cmd = [
                "az",
                "aks",
                "get-credentials",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--overwrite-existing",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return f"Credentials for AKS cluster '{cluster_name}' set successfully."
        except subprocess.CalledProcessError as e:
            # Handle errors like when az CLI isn't installed or authentication failures
            return f"Error executing Azure CLI command: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def create_aks_cluster(
        resource_group_name: str,
        cluster_name: str,
        node_count: int = 1,
        node_vm_size: str = "Standard_DS2_v2",
        kubernetes_version: str = None,
    ) -> str:
        """Create a new AKS cluster using the Azure CLI.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to create
            node_count: Number of nodes in the cluster (default: 1)
            node_vm_size: VM size for the nodes (default: Standard_DS2_v2)
            kubernetes_version: Kubernetes version to use (default: latest stable)
        """
        try:
            # Build the command
            cmd = [
                "az",
                "aks",
                "create",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--node-count",
                str(node_count),
                "--node-vm-size",
                node_vm_size,
                "--generate-ssh-keys",
            ]

            # Add kubernetes version if specified
            if kubernetes_version:
                cmd.extend(["--kubernetes-version", kubernetes_version])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"AKS cluster '{cluster_name}' created successfully."

        except subprocess.CalledProcessError as e:
            return f"Error creating AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def delete_aks_cluster(resource_group_name: str, cluster_name: str) -> str:
        """Delete an AKS cluster using the Azure CLI.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to delete
        """
        try:
            cmd = [
                "az",
                "aks",
                "delete",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--yes",  # Skip confirmation
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"AKS cluster '{cluster_name}' deletion initiated."

        except subprocess.CalledProcessError as e:
            return f"Error deleting AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def scale_aks_cluster(
        resource_group_name: str, cluster_name: str, node_count: int
    ) -> str:
        """Scale an AKS cluster by changing the number of nodes.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to scale
            node_count: New node count for the cluster
        """
        try:
            cmd = [
                "az",
                "aks",
                "scale",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--node-count",
                str(node_count),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"AKS cluster '{cluster_name}' scaled to {node_count} nodes."

        except subprocess.CalledProcessError as e:
            return f"Error scaling AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def upgrade_aks_cluster(
        resource_group_name: str, cluster_name: str, kubernetes_version: str
    ) -> str:
        """Upgrade an AKS cluster to a specific Kubernetes version.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to upgrade
            kubernetes_version: Target Kubernetes version
        """
        try:
            cmd = [
                "az",
                "aks",
                "upgrade",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--kubernetes-version",
                kubernetes_version,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"AKS cluster '{cluster_name}' upgrade to version {kubernetes_version} initiated."

        except subprocess.CalledProcessError as e:
            return f"Error upgrading AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_aks_versions(location: str = None) -> str:
        """Get available Kubernetes versions for AKS.

        Args:
            location: Azure region to check for available versions (optional)
        """
        try:
            cmd = ["az", "aks", "get-versions"]

            # Add location if specified
            if location:
                cmd.extend(["--location", location])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            versions = json.loads(result.stdout)

            formatted_output = ["Available Kubernetes versions:"]
            for orchestrator in versions.get("orchestrators", []):
                version = orchestrator.get("orchestratorVersion")
                is_preview = orchestrator.get("isPreview", False)
                is_default = orchestrator.get("default", False)

                status = []
                if is_default:
                    status.append("DEFAULT")
                if is_preview:
                    status.append("PREVIEW")

                status_str = f" ({', '.join(status)})" if status else ""
                formatted_output.append(f"- {version}{status_str}")

            return "\n".join(formatted_output)

        except subprocess.CalledProcessError as e:
            return f"Error getting AKS versions: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_aks_nodepool_list(resource_group_name: str, cluster_name: str) -> str:
        """List node pools in an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "list",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            nodepools = json.loads(result.stdout)

            if not nodepools:
                return f"No node pools found in AKS cluster '{cluster_name}'."

            formatted_output = [f"Node pools in AKS cluster '{cluster_name}':"]
            for pool in nodepools:
                formatted_output.append(f"- Name: {pool.get('name')}")
                formatted_output.append(f"  Mode: {pool.get('mode')}")
                formatted_output.append(f"  VM Size: {pool.get('vmSize')}")
                formatted_output.append(f"  Node Count: {pool.get('count')}")
                formatted_output.append(f"  OS: {pool.get('osType')}")
                formatted_output.append(
                    f"  Kubernetes Version: {pool.get('orchestratorVersion')}"
                )
                formatted_output.append(f"  Status: {pool.get('provisioningState')}")
                formatted_output.append("---")

            return "\n".join(formatted_output)

        except subprocess.CalledProcessError as e:
            return f"Error listing node pools: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def add_aks_nodepool(
        resource_group_name: str,
        cluster_name: str,
        nodepool_name: str,
        node_count: int = 1,
        node_vm_size: str = "Standard_DS2_v2",
        mode: str = "User",
    ) -> str:
        """Add a new node pool to an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            nodepool_name: Name for the new node pool
            node_count: Number of nodes in the pool (default: 1)
            node_vm_size: VM size for the nodes (default: Standard_DS2_v2)
            mode: Node pool mode (System or User, default: User)
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "add",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                nodepool_name,
                "--node-count",
                str(node_count),
                "--node-vm-size",
                node_vm_size,
                "--mode",
                mode,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Node pool '{nodepool_name}' added to AKS cluster '{cluster_name}' successfully."

        except subprocess.CalledProcessError as e:
            return f"Error adding node pool: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def delete_aks_nodepool(
        resource_group_name: str, cluster_name: str, nodepool_name: str
    ) -> str:
        """Delete a node pool from an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            nodepool_name: Name of the node pool to delete
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "delete",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                nodepool_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Node pool '{nodepool_name}' deleted from AKS cluster '{cluster_name}' successfully."

        except subprocess.CalledProcessError as e:
            return f"Error deleting node pool: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def enable_aks_addons(
        resource_group_name: str, cluster_name: str, addons: str
    ) -> str:
        """Enable add-ons for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            addons: Comma-separated list of add-ons (e.g., monitoring,virtual-node,http_application_routing,ingress-appgw)
        """
        try:
            cmd = [
                "az",
                "aks",
                "enable-addons",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--addons",
                addons,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Add-ons '{addons}' enabled for AKS cluster '{cluster_name}' successfully."

        except subprocess.CalledProcessError as e:
            return f"Error enabling add-ons: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def disable_aks_addons(
        resource_group_name: str, cluster_name: str, addons: str
    ) -> str:
        """Disable add-ons for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            addons: Comma-separated list of add-ons to disable
        """
        try:
            cmd = [
                "az",
                "aks",
                "disable-addons",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--addons",
                addons,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Add-ons '{addons}' disabled for AKS cluster '{cluster_name}' successfully."

        except subprocess.CalledProcessError as e:
            return f"Error disabling add-ons: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_aks_credentials_admin(
        cluster_name: str, resource_group_name: str
    ) -> str:
        """Get admin credentials for an AKS cluster.

        Args:
            cluster_name: Name of the AKS cluster
            resource_group_name: Name of the resource group
        """
        try:
            cmd = [
                "az",
                "aks",
                "get-credentials",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--admin",
                "--overwrite-existing",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return (
                f"Admin credentials for AKS cluster '{cluster_name}' set successfully."
            )

        except subprocess.CalledProcessError as e:
            return f"Error getting admin credentials: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def rotate_aks_certs(resource_group_name: str, cluster_name: str) -> str:
        """Rotate certificates and keys for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
        """
        try:
            cmd = [
                "az",
                "aks",
                "rotate-certs",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Certificate rotation initiated for AKS cluster '{cluster_name}'."

        except subprocess.CalledProcessError as e:
            return f"Error rotating certificates: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def install_aks_cli() -> str:
        """Download and install kubectl, the Kubernetes command-line tool.

        Args:
            None
        """
        try:
            cmd = ["az", "aks", "install-cli"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return "Successfully installed kubectl and kubelogin."

        except subprocess.CalledProcessError as e:
            return f"Error installing kubectl and kubelogin: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def start_aks_cluster(resource_group_name: str, cluster_name: str) -> str:
        """Start a previously stopped AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to start
        """
        try:
            cmd = [
                "az",
                "aks",
                "start",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"AKS cluster '{cluster_name}' is starting."

        except subprocess.CalledProcessError as e:
            return f"Error starting AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def stop_aks_cluster(resource_group_name: str, cluster_name: str) -> str:
        """Stop a running AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to stop
        """
        try:
            cmd = [
                "az",
                "aks",
                "stop",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"AKS cluster '{cluster_name}' is stopping."

        except subprocess.CalledProcessError as e:
            return f"Error stopping AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def update_aks_cluster(
        resource_group_name: str,
        cluster_name: str,
        kubernetes_version: str = None,
        auto_upgrade_channel: str = None,
        enable_node_public_ip: bool = None,
        tags: str = None,
    ) -> str:
        """Update an AKS cluster properties.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster to update
            kubernetes_version: Target Kubernetes version (optional)
            auto_upgrade_channel: Auto upgrade channel (none, patch, stable, rapid, node-image) (optional)
            enable_node_public_ip: Enable/disable nodes having public IPs (optional)
            tags: Space-separated tags in 'key[=value]' format (optional)
        """
        try:
            # Set environment variable to disable interactive prompts
            env = os.environ.copy()
            env["AZURE_CORE_NO_PROMPT"] = "true"

            cmd = [
                "az",
                "aks",
                "update",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--yes",  # Don't wait for operation to complete
            ]

            if kubernetes_version:
                cmd.extend(["--kubernetes-version", kubernetes_version])

            if auto_upgrade_channel is not None:
                cmd.extend(["--auto-upgrade-channel", auto_upgrade_channel])

            if enable_node_public_ip is not None:
                cmd.extend(
                    ["--enable-node-public-ip", str(enable_node_public_ip).lower()]
                )

            if tags:
                cmd.extend(["--tags", tags])

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, env=env
            )
            return f"AKS cluster '{cluster_name}' update initiated."

        except subprocess.CalledProcessError as e:
            return f"Error updating AKS cluster: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def check_aks_acr(
        resource_group_name: str, cluster_name: str, acr_name: str
    ) -> str:
        """Validate an Azure Container Registry is accessible from an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            acr_name: Name of the Azure Container Registry
        """
        try:
            cmd = [
                "az",
                "aks",
                "check-acr",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--acr",
                acr_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError as e:
            return f"Error checking ACR accessibility: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def aks_command_invoke(
        resource_group_name: str, cluster_name: str, command: str
    ) -> str:
        """Execute a command in the AKS cluster as an administrator.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            command: The command to execute
        """
        try:
            cmd = [
                "az",
                "aks",
                "command",
                "invoke",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
                "--command",
                command,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError as e:
            return f"Error executing cluster command: {e.stderr}"
        except json.JSONDecodeError:
            return "Error parsing command output"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def aks_nodepool_scale(
        resource_group_name: str, cluster_name: str, nodepool_name: str, node_count: int
    ) -> str:
        """Scale the node count of a node pool in an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            nodepool_name: Name of the node pool
            node_count: New node count
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "scale",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                nodepool_name,
                "--node-count",
                str(node_count),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Node pool '{nodepool_name}' in cluster '{cluster_name}' scaled to {node_count} nodes."

        except subprocess.CalledProcessError as e:
            return f"Error scaling node pool: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def aks_nodepool_upgrade(
        resource_group_name: str,
        cluster_name: str,
        nodepool_name: str,
        kubernetes_version: str,
    ) -> str:
        """Upgrade a node pool to a specific Kubernetes version.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            nodepool_name: Name of the node pool to upgrade
            kubernetes_version: Target Kubernetes version
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "upgrade",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                nodepool_name,
                "--kubernetes-version",
                kubernetes_version,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Node pool '{nodepool_name}' upgrade to version {kubernetes_version} initiated."

        except subprocess.CalledProcessError as e:
            return f"Error upgrading node pool: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def aks_nodepool_update(
        resource_group_name: str,
        cluster_name: str,
        nodepool_name: str,
        max_pods: int = None,
        enable_node_public_ip: bool = None,
        labels: str = None,
        tags: str = None,
        disable_cluster_autoscaler: bool = None,
        enable_cluster_autoscaler: bool = None,
        min_count: int = None,
        max_count: int = None,
    ) -> str:
        """Update a node pool with new properties.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            nodepool_name: Name of the node pool
            max_pods: Maximum number of pods per node (optional)
            enable_node_public_ip: Enable/disable nodes having public IPs (optional)
            labels: Comma-separated labels to apply to nodes (optional)
            tags: Space-separated tags in 'key[=value]' format for the node pool (optional)
            disable_cluster_autoscaler: Disable cluster autoscaler for this node pool (optional)
            enable_cluster_autoscaler: Enable cluster autoscaler for this node pool (optional)
            min_count: Minimum number of nodes for auto-scaling (required when enabling cluster autoscaler)
            max_count: Maximum number of nodes for auto-scaling (required when enabling cluster autoscaler)
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "update",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                nodepool_name,
                "--yes",
            ]

            if max_pods is not None:
                cmd.extend(["--max-pods", str(max_pods)])

            if enable_node_public_ip is not None:
                cmd.extend(
                    ["--enable-node-public-ip", str(enable_node_public_ip).lower()]
                )

            if labels:
                cmd.extend(["--labels", labels])

            if tags:
                cmd.extend(["--tags", tags])

            if disable_cluster_autoscaler:
                cmd.extend(["--disable-cluster-autoscaler"])

            if enable_cluster_autoscaler:
                cmd.extend(["--enable-cluster-autoscaler"])

                if min_count is None or max_count is None:
                    return "Error: min_count and max_count are required when enabling cluster autoscaler"

                cmd.extend(
                    ["--min-count", str(min_count), "--max-count", str(max_count)]
                )

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Node pool '{nodepool_name}' updated successfully."

        except subprocess.CalledProcessError as e:
            return f"Error updating node pool: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def aks_nodepool_show(
        resource_group_name: str, cluster_name: str, nodepool_name: str
    ) -> str:
        """Show details of a node pool in an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            nodepool_name: Name of the node pool
        """
        try:
            cmd = [
                "az",
                "aks",
                "nodepool",
                "show",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                nodepool_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            nodepool = json.loads(result.stdout)

            formatted_output = [f"Node pool '{nodepool_name}' details:"]
            formatted_output.append(f"Mode: {nodepool.get('mode')}")
            formatted_output.append(f"VM Size: {nodepool.get('vmSize')}")
            formatted_output.append(f"Node Count: {nodepool.get('count')}")
            formatted_output.append(f"OS Type: {nodepool.get('osType')}")
            formatted_output.append(
                f"Kubernetes Version: {nodepool.get('orchestratorVersion')}"
            )
            formatted_output.append(f"Status: {nodepool.get('provisioningState')}")
            formatted_output.append(f"Max Pods: {nodepool.get('maxPods')}")

            if nodepool.get("nodeLabels"):
                formatted_output.append("Labels:")
                for k, v in nodepool.get("nodeLabels", {}).items():
                    formatted_output.append(f"  {k}: {v}")

            if nodepool.get("nodeTaints"):
                formatted_output.append("Taints:")
                for taint in nodepool.get("nodeTaints", []):
                    formatted_output.append(f"  {taint}")

            return "\n".join(formatted_output)

        except subprocess.CalledProcessError as e:
            return f"Error getting node pool details: {e.stderr}"
        except json.JSONDecodeError:
            return "Error parsing node pool information"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def create_aks_maintenance_config(
        resource_group_name: str,
        cluster_name: str,
        config_name: str,
        schedule_type: str,
        day_of_week: str = None,
        day_of_month: int = None,
        start_hour: int = None,
        duration_hours: int = 4,
    ) -> str:
        """Create a maintenance configuration for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            config_name: Name for the maintenance configuration
            schedule_type: Schedule type (Weekly, AbsoluteMonthly, or RelativeMonthly)
            day_of_week: Day of week for Weekly schedule (Monday-Sunday)
            day_of_month: Day of month for AbsoluteMonthly schedule (1-28)
            start_hour: Hour when maintenance should start (0-23)
            duration_hours: Maximum duration in hours (default: 4)
        """
        try:
            cmd = [
                "az",
                "aks",
                "maintenanceconfiguration",
                "create",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                config_name,
                "--schedule-type",
                schedule_type,
            ]

            if schedule_type.lower() == "weekly" and day_of_week:
                cmd.extend(["--day-of-week", day_of_week])
            elif schedule_type.lower() == "absolutemonthly" and day_of_month:
                cmd.extend(["--day-of-month", str(day_of_month)])

            if start_hour is not None:
                cmd.extend(["--start-hour", str(start_hour)])

            if duration_hours is not None:
                cmd.extend(["--duration-hours", str(duration_hours)])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Maintenance configuration '{config_name}' created for cluster '{cluster_name}'."

        except subprocess.CalledProcessError as e:
            return f"Error creating maintenance configuration: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def list_aks_maintenance_configs(
        resource_group_name: str, cluster_name: str
    ) -> str:
        """List maintenance configurations for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
        """
        try:
            cmd = [
                "az",
                "aks",
                "maintenanceconfiguration",
                "list",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            configs = json.loads(result.stdout)

            if not configs:
                return f"No maintenance configurations found for AKS cluster '{cluster_name}'."

            formatted_output = [
                f"Maintenance configurations for cluster '{cluster_name}':"
            ]
            for config in configs:
                formatted_output.append(f"Name: {config.get('name')}")

                window = config.get("properties", {}).get("maintenanceWindow", {})
                schedule = window.get("schedule", {})

                formatted_output.append(
                    f"  Schedule Type: {schedule.get('scheduleType')}"
                )

                if "dayOfWeek" in schedule:
                    formatted_output.append(
                        f"  Day of Week: {schedule.get('dayOfWeek')}"
                    )
                if "dayOfMonth" in schedule:
                    formatted_output.append(
                        f"  Day of Month: {schedule.get('dayOfMonth')}"
                    )

                formatted_output.append(
                    f"  Start Hour (UTC): {schedule.get('startHour', 'Not set')}"
                )
                formatted_output.append(
                    f"  Duration (hours): {schedule.get('durationHours', 'Not set')}"
                )
                formatted_output.append("---")

            return "\n".join(formatted_output)

        except subprocess.CalledProcessError as e:
            return f"Error listing maintenance configurations: {e.stderr}"
        except json.JSONDecodeError:
            return "Error parsing maintenance configurations"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def delete_aks_maintenance_config(
        resource_group_name: str, cluster_name: str, config_name: str
    ) -> str:
        """Delete a maintenance configuration for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
            config_name: Name of the maintenance configuration to delete
        """
        try:
            cmd = [
                "az",
                "aks",
                "maintenanceconfiguration",
                "delete",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--name",
                config_name,
                "--yes",  # Skip confirmation
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"Maintenance configuration '{config_name}' deleted."

        except subprocess.CalledProcessError as e:
            return f"Error deleting maintenance configuration: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    @mcp.tool()
    async def get_aks_upgrade_profile(
        resource_group_name: str, cluster_name: str
    ) -> str:
        """Get available upgrade versions for an AKS cluster.

        Args:
            resource_group_name: Name of the resource group
            cluster_name: Name of the AKS cluster
        """
        try:
            cmd = [
                "az",
                "aks",
                "get-upgrades",
                "--resource-group",
                resource_group_name,
                "--name",
                cluster_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            upgrade_data = json.loads(result.stdout)

            control_plane_profile = upgrade_data.get("controlPlaneProfile", {})
            current_version = control_plane_profile.get("kubernetesVersion", "Unknown")
            upgrades = control_plane_profile.get("upgrades", [])

            formatted_output = [f"AKS cluster '{cluster_name}' upgrade profile:"]
            formatted_output.append(f"Current Kubernetes version: {current_version}")

            if upgrades:
                formatted_output.append("Available upgrade versions:")
                for upgrade in upgrades:
                    version = upgrade.get("kubernetesVersion", "Unknown")
                    is_preview = upgrade.get("isPreview", False)
                    status = " (PREVIEW)" if is_preview else ""
                    formatted_output.append(f"- {version}{status}")
            else:
                formatted_output.append("No upgrades available.")

            return "\n".join(formatted_output)

        except subprocess.CalledProcessError as e:
            return f"Error getting upgrade profile: {e.stderr}"
        except json.JSONDecodeError:
            return "Error parsing upgrade information"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
