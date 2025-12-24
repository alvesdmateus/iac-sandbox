from abc import ABC, abstractmethod
from typing import Any
import pulumi


class CloudProvider(ABC):
    """Abstract interface for cloud provider resources."""
    
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.region = config.get("region")
        self.project = config.get("project")
    
    @abstractmethod
    def create_kubernetes_cluster(self, name: str) -> Any:
        """Provision a managed Kubernetes cluster."""
        pass
    
    @abstractmethod
    def get_kubeconfig(self, cluster: Any) -> pulumi.Output[str]:
        """Return kubeconfig for cluster access."""
        pass