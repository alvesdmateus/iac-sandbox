import pulumi
import pulumi_kubernetes as k8s
from providers.gcp import GCPProvider
from providers.base import CloudProvider
from application.sudoku_app import deploy_sudoku_app


def get_provider(name: str, config: dict) -> CloudProvider:
    """Factory pattern for provider instantiation."""
    providers = {
        "gcp": GCPProvider,
        # Future: "aws": AWSProvider, "azure": AzureProvider
    }
    
    if name not in providers:
        raise ValueError(f"Unsupported provider: {name}. Available: {list(providers.keys())}")
    
    return providers[name](config)


# Load configuration
config = pulumi.Config()
gcp_config = pulumi.Config("gcp")

provider_name = config.require("provider")
region = config.require("region")
app_image = config.require("app_image")
project_id = gcp_config.require("project")
stack = pulumi.get_stack()

# Instantiate cloud provider
cloud = get_provider(provider_name, {
    "region": region,
    "project": project_id
})

# Provision Kubernetes cluster
cluster = cloud.create_kubernetes_cluster(name=f"sandbox-{stack}")
# Configure Kubernetes provider using GCP cluster credentials directly
# Configure Kubernetes provider using GCP cluster credentials directly
# Configure Kubernetes provider using GCP cluster credentials directly
kubeconfig = pulumi.Output.all(
    cluster.name,
    cluster.endpoint,
    cluster.master_auth
).apply(lambda args: f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {args[2]['cluster_ca_certificate']}
    server: https://{args[1]}
  name: {args[0]}
contexts:
- context:
    cluster: {args[0]}
    user: {args[0]}
  name: {args[0]}
current-context: {args[0]}
kind: Config
users:
- name: {args[0]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      provideClusterInfo: true
      interactiveMode: Never
""")

k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=kubeconfig,
    opts=pulumi.ResourceOptions(depends_on=[cluster])
)

# Deploy application
deploy_sudoku_app(
    provider=k8s_provider,
    namespace="default",
    image=app_image,
    replicas=1
)

# Export cluster metadata
pulumi.export("cluster_name", cluster.name)
pulumi.export("cluster_endpoint", cluster.endpoint)