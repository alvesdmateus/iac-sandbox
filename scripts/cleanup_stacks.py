#!/usr/bin/env python3
"""Destroy Pulumi stacks past their TTL."""

import subprocess
import json
from datetime import datetime, timezone

def get_stacks():
    result = subprocess.run(
        ["pulumi", "stack", "ls", "--json"],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def should_destroy(stack_name: str) -> bool:
    result = subprocess.run(
        ["pulumi", "stack", "tag", "get", "expires_at", "--stack", stack_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return False  # No TTL tag
    
    expires_at = datetime.fromisoformat(result.stdout.strip())
    return datetime.now(timezone.utc) > expires_at

def destroy_stack(stack_name: str):
    print(f"Destroying stack: {stack_name}")
    subprocess.run(
        ["pulumi", "destroy", "--yes", "--stack", stack_name],
        check=True
    )
    subprocess.run(
        ["pulumi", "stack", "rm", "--yes", stack_name],
        check=True
    )

if __name__ == "__main__":
    for stack in get_stacks():
        if stack["name"].startswith("dev-") and should_destroy(stack["name"]):
            destroy_stack(stack["name"])