"""Stack management API endpoints."""
import logging
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.stack import (
    StackSummary,
    StackInfo,
    Resource,
    CreateStackRequest,
    UpdateStackConfigRequest,
    DeploymentResult,
    DeploymentSummary,
)
from ..services.pulumi_service import pulumi_service


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stacks", response_model=List[StackSummary])
async def list_stacks():
    """List all Pulumi stacks."""
    try:
        stacks = await pulumi_service.list_stacks()
        return stacks
    except Exception as e:
        logger.error(f"Error listing stacks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stacks/{stack_name}", response_model=StackInfo)
async def get_stack(stack_name: str):
    """Get detailed information about a stack."""
    try:
        stack_info = await pulumi_service.get_stack_info(stack_name)
        if not stack_info:
            raise HTTPException(status_code=404, detail=f"Stack not found: {stack_name}")
        return stack_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stack {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stacks", response_model=StackInfo, status_code=201)
async def create_stack(request: CreateStackRequest):
    """Create a new Pulumi stack."""
    try:
        # Create or get stack
        stack = await pulumi_service.get_or_create_stack(request.name)

        # Update configuration if provided
        if request.config:
            await pulumi_service.update_stack_config(request.name, request.config)

        # Get stack info
        stack_info = await pulumi_service.get_stack_info(request.name)
        return stack_info
    except Exception as e:
        logger.error(f"Error creating stack {request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/stacks/{stack_name}")
async def delete_stack(stack_name: str):
    """Delete a stack (must be empty first)."""
    try:
        success = await pulumi_service.delete_stack(stack_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete stack")
        return JSONResponse(
            content={"message": f"Stack {stack_name} deleted successfully"}
        )
    except Exception as e:
        logger.error(f"Error deleting stack {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/stacks/{stack_name}/config")
async def update_stack_config(stack_name: str, request: UpdateStackConfigRequest):
    """Update stack configuration."""
    try:
        success = await pulumi_service.update_stack_config(stack_name, request.config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update configuration")

        stack_info = await pulumi_service.get_stack_info(stack_name)
        return stack_info
    except Exception as e:
        logger.error(f"Error updating config for {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stacks/{stack_name}/outputs")
async def get_stack_outputs(stack_name: str):
    """Get stack outputs."""
    try:
        outputs = await pulumi_service.get_stack_outputs(stack_name)
        return JSONResponse(content={"outputs": outputs})
    except Exception as e:
        logger.error(f"Error getting outputs for {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stacks/{stack_name}/resources", response_model=List[Resource])
async def get_stack_resources(stack_name: str):
    """Get all resources in a stack."""
    try:
        resources = await pulumi_service.get_stack_resources(stack_name)
        return resources
    except Exception as e:
        logger.error(f"Error getting resources for {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stacks/{stack_name}/preview")
async def preview_stack(stack_name: str):
    """
    Preview changes to a stack without applying them.

    Note: This is a synchronous operation. For real-time updates,
    use the WebSocket connection to subscribe to stack events.
    """
    try:
        deployment_id = str(uuid.uuid4())

        # For now, run preview synchronously
        # TODO: Implement async with WebSocket streaming
        result = await pulumi_service.preview_stack(stack_name)

        return DeploymentResult(
            deployment_id=deployment_id,
            stack_name=stack_name,
            operation="preview",
            status="completed",
            summary=DeploymentSummary(
                created=result.change_summary.get("create", 0) if hasattr(result, 'change_summary') else 0,
                updated=result.change_summary.get("update", 0) if hasattr(result, 'change_summary') else 0,
                deleted=result.change_summary.get("delete", 0) if hasattr(result, 'change_summary') else 0,
                unchanged=result.change_summary.get("same", 0) if hasattr(result, 'change_summary') else 0,
            )
        )
    except Exception as e:
        logger.error(f"Error previewing stack {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stacks/{stack_name}/up")
async def deploy_stack(stack_name: str, background_tasks: BackgroundTasks):
    """
    Deploy a stack (apply all changes).

    Note: This starts the deployment. Subscribe to WebSocket for real-time updates.
    """
    try:
        deployment_id = str(uuid.uuid4())

        # For now, run deployment synchronously
        # TODO: Implement async with WebSocket streaming
        result = await pulumi_service.up_stack(stack_name)

        # Get outputs
        try:
            outputs = await pulumi_service.get_stack_outputs(stack_name)
        except:
            outputs = {}

        return DeploymentResult(
            deployment_id=deployment_id,
            stack_name=stack_name,
            operation="up",
            status="completed",
            summary=DeploymentSummary(
                created=result.summary.resource_changes.get("create", 0) if hasattr(result.summary, 'resource_changes') else 0,
                updated=result.summary.resource_changes.get("update", 0) if hasattr(result.summary, 'resource_changes') else 0,
                deleted=result.summary.resource_changes.get("delete", 0) if hasattr(result.summary, 'resource_changes') else 0,
                unchanged=result.summary.resource_changes.get("same", 0) if hasattr(result.summary, 'resource_changes') else 0,
            ),
            outputs=outputs,
        )
    except Exception as e:
        logger.error(f"Error deploying stack {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stacks/{stack_name}/destroy")
async def destroy_stack(stack_name: str):
    """
    Destroy all resources in a stack.

    Note: This starts the destroy operation. Subscribe to WebSocket for real-time updates.
    """
    try:
        deployment_id = str(uuid.uuid4())

        # For now, run destroy synchronously
        # TODO: Implement async with WebSocket streaming
        result = await pulumi_service.destroy_stack(stack_name)

        return DeploymentResult(
            deployment_id=deployment_id,
            stack_name=stack_name,
            operation="destroy",
            status="completed",
            summary=DeploymentSummary(
                deleted=result.summary.resource_changes.get("delete", 0) if hasattr(result.summary, 'resource_changes') else 0,
            ),
        )
    except Exception as e:
        logger.error(f"Error destroying stack {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stacks/{stack_name}/refresh")
async def refresh_stack(stack_name: str):
    """Refresh stack state from actual infrastructure."""
    try:
        await pulumi_service.refresh_stack(stack_name)
        stack_info = await pulumi_service.get_stack_info(stack_name)
        return stack_info
    except Exception as e:
        logger.error(f"Error refreshing stack {stack_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
