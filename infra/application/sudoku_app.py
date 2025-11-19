import pulumi
import pulumi_kubernetes as k8s
from typing import Dict

def deploy_sudoku_app(
    provider: k8s.Provider, 
    namespace: str,
    image: str,
    replicas: int = 2
) -> k8s.apps.v1.Deployment:
    """Deploy sudoku TypeScript web app with LoadBalancer service."""
    
    app_labels = {"app": "sudoku-app"}
    
    # Deployment with resource limits (SRE best practice)
    deployment = k8s.apps.v1.Deployment(
        "sudoku-deployment",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            namespace=namespace,
            labels=app_labels,
        ),
        spec=k8s.apps.v1.DeploymentSpecArgs(
            replicas=replicas,
            selector=k8s.meta.v1.LabelSelectorArgs(match_labels=app_labels),
            template=k8s.core.v1.PodTemplateSpecArgs(
                metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels),
                spec=k8s.core.v1.PodSpecArgs(
                    containers=[k8s.core.v1.ContainerArgs(
                        name="sudoku-app",
                        image=image,
                        ports=[k8s.core.v1.ContainerPortArgs(container_port=3000)],
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"cpu": "100m", "memory": "128Mi"},
                            limits={"cpu": "200m", "memory": "256Mi"},
                        ),
                    )],
                ),
            ),
        ),
        opts=pulumi.ResourceOptions(provider=provider)
    )
    
    # LoadBalancer service (auto-provisions GCP LB)
    service = k8s.core.v1.Service(
        "sudoku-service",
        metadata=k8s.meta.v1.ObjectMetaArgs(namespace=namespace),
        spec=k8s.core.v1.ServiceSpecArgs(
            type="LoadBalancer",
            selector=app_labels,
            ports=[k8s.core.v1.ServicePortArgs(
                port=80,
                target_port=3000,
            )],
        ),
        opts=pulumi.ResourceOptions(provider=provider)
    )
    
    # Export public URL
    pulumi.export("sudoku_url", service.status.load_balancer.ingress[0].ip.apply(
        lambda ip: f"http://{ip}"
    ))
    
    return deployment