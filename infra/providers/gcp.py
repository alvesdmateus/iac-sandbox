import pulumi
import pulumi_gcp as gcp
from .base import CloudProvider
from typing import Any


class GCPProvider(CloudProvider):
    """GCP-specific Kubernetes using GKE Autopilot for cost optimization."""
    
    def create_kubernetes_cluster(self, name: str) -> gcp.container.Cluster:
        # GKE Autopilot: Free tier eligible, minimal management overhead
        cluster = gcp.container.Cluster(
            name,
            name=name,
            location=self.region,
            enable_autopilot=True,
            deletion_protection=False,  # Required for ephemeral environments
            initial_node_count=1,
            opts=pulumi.ResourceOptions(protect=False)
        )
        return cluster
    
    def get_kubeconfig(self, cluster: gcp.container.Cluster) -> pulumi.Output[str]:
        """Generate kubeconfig for GKE cluster access."""
        return pulumi.Output.all(
            cluster.name,
            cluster.endpoint,
            cluster.master_auth
        ).apply(
            lambda args: self._build_kubeconfig(args[0], args[1], args[2])
        )
    
    def _build_kubeconfig(self, name: str, endpoint: str, auth: Any) -> str:
        """Build kubeconfig with gke-gcloud-auth-plugin for authentication."""
        context = f"gke_{self.project}_{self.region}_{name}"
        
        return f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {auth.cluster_ca_certificate}
    server: https://{endpoint}
  name: {context}
contexts:
- context:
    cluster: {context}
    user: {context}
  name: {context}
current-context: {context}
kind: Config
users:
- name: {context}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      provideClusterInfo: true
"""