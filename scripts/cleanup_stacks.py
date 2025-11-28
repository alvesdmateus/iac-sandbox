#!/usr/bin/env python3
"""Destroy Pulumi stacks past their TTL expiration date."""

import subprocess
import json
import sys
from datetime import datetime, timezone


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Execute shell command and return result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check
    )


def get_stacks() -> list[dict]:
    """Fetch all Pulumi stacks in JSON format."""
    result = run_command(["pulumi", "stack", "ls", "--json", "--all"])
    return json.loads(result.stdout)


def get_stack_tag(stack_name: str, tag_name: str) -> str | None:
    """Retrieve a specific tag value from a stack."""
    result = run_command(
        ["pulumi", "stack", "tag", "get", tag_name, "--stack", stack_name],
        check=False
    )
    
    if result.returncode != 0:
        return None
    
    return result.stdout.strip()


def should_destroy(stack_name: str) -> bool:
    """Check if stack has expired based on TTL tag."""
    expires_at_str = get_stack_tag(stack_name, "expires_at")
    
    if not expires_at_str:
        print(f"⏭️  Skipping {stack_name}: No expiration tag")
        return False
    
    try:
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        if now > expires_at:
            print(f"🗑️  {stack_name} expired at {expires_at_str}")
            return True
        else:
            remaining = expires_at - now
            print(f"⏳ {stack_name} expires in {remaining.days}d {remaining.seconds//3600}h")
            return False
    
    except ValueError as e:
        print(f"⚠️  Invalid date format for {stack_name}: {e}")
        return False


def destroy_stack(stack_name: str) -> None:
    """Destroy and remove a Pulumi stack."""
    print(f"🔥 Destroying stack: {stack_name}")
    
    try:
        run_command(["pulumi", "destroy", "--yes", "--stack", stack_name])
        run_command(["pulumi", "stack", "rm", "--yes", stack_name])
        print(f"✅ Successfully destroyed {stack_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to destroy {stack_name}: {e.stderr}")
        sys.exit(1)


def main():
    """Main cleanup orchestration."""
    print("🔍 Scanning for expired stacks...")
    
    stacks = get_stacks()
    dev_stacks = [s for s in stacks if s["name"].startswith("dev-")]
    
    if not dev_stacks:
        print("✅ No dev stacks found")
        return
    
    print(f"📋 Found {len(dev_stacks)} dev stack(s)")
    
    destroyed_count = 0
    for stack in dev_stacks:
        stack_name = stack["name"]
        if should_destroy(stack_name):
            destroy_stack(stack_name)
            destroyed_count += 1
    
    print(f"\n🎯 Cleanup complete: {destroyed_count} stack(s) destroyed")


if __name__ == "__main__":
    main()