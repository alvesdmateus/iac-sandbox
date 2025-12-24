"""Pulumi Automation API service for programmatic infrastructure management."""
import os
import asyncio
import logging
from typing import Optional, Dict, List, Callable, Any
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime

import pulumi
from pulumi import automation as auto

from ..config import settings


logger = logging.getLogger(__name__)


class PulumiService:
    """Wrapper around Pulumi Automation API for programmatic infrastructure management."""

    def __init__(self, work_dir: Optional[Path] = None):
        """
        Initialize Pulumi service.

        Args:
            work_dir: Directory containing Pulumi infrastructure code.
                     Defaults to settings.INFRA_DIR.
        """
        self.work_dir = str(work_dir or settings.INFRA_DIR)
        self.executor = ThreadPoolExecutor(max_workers=4)
        logger.info(f"Initialized PulumiService with work_dir: {self.work_dir}")

    async def list_stacks(self) -> List[Dict[str, Any]]:
        """
        List all Pulumi stacks in the workspace.

        Returns:
            List of stack summaries with name, last update, resource count.
        """

        def _sync_list_stacks():
            try:
                ws = auto.LocalWorkspace(work_dir=self.work_dir)
                stacks = ws.list_stacks()

                stack_list = []
                for stack_info in stacks:
                    stack_list.append({
                        "name": stack_info.name,
                        "current": stack_info.current,
                        "last_update": stack_info.last_update,
                        "resource_count": stack_info.resource_count,
                        "url": stack_info.url,
                    })

                return stack_list
            except Exception as e:
                logger.error(f"Error listing stacks: {e}")
                return []

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_list_stacks
        )

    async def get_or_create_stack(
        self, stack_name: str, project_name: str = "iac-sandbox"
    ) -> auto.Stack:
        """
        Get existing stack or create new one with default configuration.

        Args:
            stack_name: Name of the stack (e.g., "dev-username")
            project_name: Name of the Pulumi project

        Returns:
            Pulumi Stack object
        """

        def _sync_get_or_create():
            try:
                # Try to select existing stack
                stack = auto.select_stack(
                    stack_name=stack_name,
                    work_dir=self.work_dir,
                )
                logger.info(f"Selected existing stack: {stack_name}")
            except auto.StackNotFoundError:
                # Create new stack if not found
                logger.info(f"Creating new stack: {stack_name}")
                stack = auto.create_stack(
                    stack_name=stack_name,
                    work_dir=self.work_dir,
                )

                # Set default configuration
                gcp_project = settings.GCP_PROJECT_ID or os.environ.get("GCP_PROJECT_ID")
                if gcp_project:
                    stack.set_config("gcp:project", auto.ConfigValue(value=gcp_project))
                    stack.set_config("iac-sandbox:provider", auto.ConfigValue(value="gcp"))
                    stack.set_config("iac-sandbox:region", auto.ConfigValue(value=settings.GCP_REGION))
                    stack.set_config(
                        "iac-sandbox:app_image",
                        auto.ConfigValue(
                            value=f"us-central1-docker.pkg.dev/{gcp_project}/sudoku-repo/sudoku-app:master"
                        ),
                    )
                    logger.info(f"Configured stack {stack_name} with default settings")

            return stack

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_get_or_create
        )

    async def get_stack_info(self, stack_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a stack.

        Args:
            stack_name: Name of the stack

        Returns:
            Dictionary with stack details or None if not found
        """

        def _sync_get_info():
            try:
                stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)

                # Get stack configuration
                config = stack.get_all_config()
                config_dict = {k: v.value for k, v in config.items()}

                # Get stack outputs
                try:
                    outputs = stack.outputs()
                    outputs_dict = {k: v.value for k, v in outputs.items()}
                except Exception:
                    outputs_dict = {}

                # Get stack info from workspace
                ws = auto.LocalWorkspace(work_dir=self.work_dir)
                stack_summaries = ws.list_stacks()
                stack_summary = next((s for s in stack_summaries if s.name == stack_name), None)

                return {
                    "name": stack_name,
                    "config": config_dict,
                    "outputs": outputs_dict,
                    "last_update": stack_summary.last_update if stack_summary else None,
                    "resource_count": stack_summary.resource_count if stack_summary else 0,
                    "url": stack_summary.url if stack_summary else None,
                }
            except auto.StackNotFoundError:
                logger.warning(f"Stack not found: {stack_name}")
                return None
            except Exception as e:
                logger.error(f"Error getting stack info: {e}")
                return None

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_get_info
        )

    async def preview_stack(
        self,
        stack_name: str,
        on_output: Optional[Callable[[str], None]] = None,
        on_event: Optional[Callable[[auto.EngineEvent], None]] = None,
    ) -> auto.PreviewResult:
        """
        Preview changes to stack without applying them.

        Args:
            stack_name: Name of the stack
            on_output: Callback for output messages
            on_event: Callback for engine events

        Returns:
            Preview result with change summary
        """

        def _sync_preview():
            stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
            logger.info(f"Previewing stack: {stack_name}")

            return stack.preview(on_output=on_output, on_event=on_event)

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_preview
        )

    async def up_stack(
        self,
        stack_name: str,
        on_output: Optional[Callable[[str], None]] = None,
        on_event: Optional[Callable[[auto.EngineEvent], None]] = None,
    ) -> auto.UpResult:
        """
        Deploy stack by applying all changes.

        Args:
            stack_name: Name of the stack
            on_output: Callback for output messages
            on_event: Callback for engine events

        Returns:
            Deployment result with summary
        """

        def _sync_up():
            stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
            logger.info(f"Deploying stack: {stack_name}")

            return stack.up(on_output=on_output, on_event=on_event)

        return await asyncio.get_event_loop().run_in_executor(self.executor, _sync_up)

    async def destroy_stack(
        self,
        stack_name: str,
        on_output: Optional[Callable[[str], None]] = None,
        on_event: Optional[Callable[[auto.EngineEvent], None]] = None,
    ) -> auto.DestroyResult:
        """
        Destroy all resources in stack.

        Args:
            stack_name: Name of the stack
            on_output: Callback for output messages
            on_event: Callback for engine events

        Returns:
            Destroy result with summary
        """

        def _sync_destroy():
            stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
            logger.info(f"Destroying stack: {stack_name}")

            return stack.destroy(on_output=on_output, on_event=on_event)

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_destroy
        )

    async def refresh_stack(
        self,
        stack_name: str,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> auto.RefreshResult:
        """
        Refresh stack state from actual infrastructure.

        Args:
            stack_name: Name of the stack
            on_output: Callback for output messages

        Returns:
            Refresh result
        """

        def _sync_refresh():
            stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
            logger.info(f"Refreshing stack: {stack_name}")

            return stack.refresh(on_output=on_output)

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_refresh
        )

    async def get_stack_outputs(self, stack_name: str) -> Dict[str, Any]:
        """
        Get stack outputs.

        Args:
            stack_name: Name of the stack

        Returns:
            Dictionary of output names to values
        """

        def _sync_outputs():
            stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
            outputs = stack.outputs()
            return {k: v.value for k, v in outputs.items()}

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_outputs
        )

    async def get_stack_resources(self, stack_name: str) -> List[Dict[str, Any]]:
        """
        Get all resources in stack from exported state.

        Args:
            stack_name: Name of the stack

        Returns:
            List of resources with URN, type, properties, dependencies
        """

        def _sync_resources():
            stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
            state = stack.export_stack()

            resources = []
            if state.deployment and state.deployment.get("resources"):
                for resource in state.deployment["resources"]:
                    resources.append({
                        "urn": resource.get("urn"),
                        "type": resource.get("type"),
                        "id": resource.get("id"),
                        "parent": resource.get("parent"),
                        "dependencies": resource.get("dependencies", []),
                        "properties": resource.get("outputs", {}),
                        "inputs": resource.get("inputs", {}),
                    })

            return resources

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_resources
        )

    async def delete_stack(self, stack_name: str) -> bool:
        """
        Delete a stack (must be empty first).

        Args:
            stack_name: Name of the stack to delete

        Returns:
            True if successful
        """

        def _sync_delete():
            try:
                stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)
                stack.workspace.remove_stack(stack_name)
                logger.info(f"Deleted stack: {stack_name}")
                return True
            except Exception as e:
                logger.error(f"Error deleting stack {stack_name}: {e}")
                return False

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_delete
        )

    async def update_stack_config(
        self, stack_name: str, config: Dict[str, str]
    ) -> bool:
        """
        Update stack configuration values.

        Args:
            stack_name: Name of the stack
            config: Dictionary of config keys to values

        Returns:
            True if successful
        """

        def _sync_update_config():
            try:
                stack = auto.select_stack(stack_name=stack_name, work_dir=self.work_dir)

                for key, value in config.items():
                    stack.set_config(key, auto.ConfigValue(value=value))

                logger.info(f"Updated config for stack {stack_name}: {list(config.keys())}")
                return True
            except Exception as e:
                logger.error(f"Error updating config for {stack_name}: {e}")
                return False

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _sync_update_config
        )


# Global instance
pulumi_service = PulumiService()
