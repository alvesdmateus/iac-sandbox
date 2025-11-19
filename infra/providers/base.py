from abc import ABC, abstractmethod
from typing import Dict, Any
import pulumi

class CloudProvider(ABC):
    """Abstract interface for cloud provider resources."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.region = config.get("region")
    
    @abstractmethod
    def create_kubernetes_cluster(self, name: str, node_count: int) -> Any:
        """Provision a managed Kubernetes cluster."""
        pass
    
    @abstractmethod
    def get_kubeconfig(self, cluster: Any) -> pulumi.Output[str]:
        """Return kubeconfig for cluster access."""
        pass