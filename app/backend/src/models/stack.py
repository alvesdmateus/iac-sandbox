"""Pydantic models for stack operations."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class StackConfig(BaseModel):
    """Stack configuration."""
    provider: str = Field(default="gcp", description="Cloud provider")
    region: str = Field(default="us-central1", description="Deployment region")
    app_image: str = Field(description="Container image to deploy")


class StackSummary(BaseModel):
    """Summary of a stack."""
    name: str = Field(description="Stack name")
    current: bool = Field(default=False, description="Whether this is the current stack")
    last_update: Optional[str] = Field(None, description="Last update timestamp")
    resource_count: int = Field(default=0, description="Number of resources")
    url: Optional[str] = Field(None, description="Pulumi console URL")


class StackInfo(BaseModel):
    """Detailed stack information."""
    name: str = Field(description="Stack name")
    config: Dict[str, Any] = Field(default_factory=dict, description="Stack configuration")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Stack outputs")
    last_update: Optional[str] = Field(None, description="Last update timestamp")
    resource_count: int = Field(default=0, description="Number of resources")
    url: Optional[str] = Field(None, description="Pulumi console URL")


class Resource(BaseModel):
    """Infrastructure resource."""
    urn: str = Field(description="Pulumi URN")
    type: str = Field(description="Resource type")
    id: Optional[str] = Field(None, description="Cloud provider resource ID")
    parent: Optional[str] = Field(None, description="Parent resource URN")
    dependencies: List[str] = Field(default_factory=list, description="Dependency URNs")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Resource properties")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Resource inputs")


class CreateStackRequest(BaseModel):
    """Request to create a new stack."""
    name: str = Field(description="Stack name", min_length=1)
    config: Optional[Dict[str, str]] = Field(None, description="Initial configuration")


class UpdateStackConfigRequest(BaseModel):
    """Request to update stack configuration."""
    config: Dict[str, str] = Field(description="Configuration key-value pairs")


class StackOperation(BaseModel):
    """Stack operation (preview, up, destroy)."""
    operation: str = Field(description="Operation type: preview, up, destroy, refresh")


class DeploymentSummary(BaseModel):
    """Summary of a deployment operation."""
    created: int = Field(default=0, description="Resources created")
    updated: int = Field(default=0, description="Resources updated")
    deleted: int = Field(default=0, description="Resources deleted")
    unchanged: int = Field(default=0, description="Resources unchanged")


class DeploymentResult(BaseModel):
    """Result of a deployment operation."""
    deployment_id: str = Field(description="Unique deployment ID")
    stack_name: str = Field(description="Stack name")
    operation: str = Field(description="Operation type")
    status: str = Field(description="Status: running, completed, failed")
    summary: Optional[DeploymentSummary] = Field(None, description="Operation summary")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Stack outputs")
    error: Optional[str] = Field(None, description="Error message if failed")
