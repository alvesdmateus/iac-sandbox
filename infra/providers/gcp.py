import pulumi
import pulumi_gcp as gcp
from .base import CloudProvider
from typing import Dict, Any

class GCPProvider(CloudProvider):
    """GCP-specific Kubernetes cluster using GKE Autopilot (free tier eligible)."""
    
    def create_kubernetes_cluster(self, name: str, node_count: int) -> gcp.container.Cluster:
        # GKE Autopilot minimizes costs and management overhead
        cluster = gcp.container.Cluster(
            name,
            name=name,
            location=self.region,
            enable_autopilot=True,  # Free tier: 1 zonal cluster
            deletion_protection=False,  # Allow ephemeral teardown
            initial_node_count=1,
            opts=pulumi.ResourceOptions(
                protect=False,  # SRE best practice: explicit protection policy
            )
        )
        return cluster
    
    def get_kubeconfig(self, cluster: gcp.container.Cluster) -> pulumi.Output[str]:
        return pulumi.Output.all(
            cluster.name, 
            cluster.endpoint, 
            cluster.master_auth
        ).apply(
            lambda args: self._generate_kubeconfig(args[0], args[1], args[2])
        )
    
    def _generate_kubeconfig(self, name: str, endpoint: str, auth: Any) -> str:
        return f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {auth.cluster_ca_certificate}
    server: https://{endpoint}
  name: {name}
contexts:
- context:
    cluster: {name}
    user: {name}
  name: {name}
current-context: {name}
kind: Config
users:
- name: {name}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      provideClusterInfo: true
"""