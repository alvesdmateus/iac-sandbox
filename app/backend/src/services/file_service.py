"""File management service for infrastructure code."""
import ast
import logging
from pathlib import Path
from typing import List, Dict, Optional
import aiofiles
import os

from ..config import settings


logger = logging.getLogger(__name__)


class FileService:
    """Manage infrastructure code files with validation and security."""

    def __init__(self, infra_dir: Optional[Path] = None):
        """
        Initialize file service.

        Args:
            infra_dir: Root directory for infrastructure files.
                      Defaults to settings.INFRA_DIR.
        """
        self.infra_dir = Path(infra_dir or settings.INFRA_DIR).resolve()
        logger.info(f"Initialized FileService with infra_dir: {self.infra_dir}")

        # Ensure directory exists
        if not self.infra_dir.exists():
            raise ValueError(f"Infrastructure directory does not exist: {self.infra_dir}")

    def _is_safe_path(self, file_path: str) -> bool:
        """
        Check if file path is within infra directory (security check).

        Args:
            file_path: Relative path to check

        Returns:
            True if path is safe
        """
        try:
            full_path = (self.infra_dir / file_path).resolve()
            return full_path.is_relative_to(self.infra_dir)
        except (ValueError, OSError):
            return False

    async def list_files(self, directory: str = "", pattern: str = "*.py") -> List[Dict[str, any]]:
        """
        List all files matching pattern in directory.

        Args:
            directory: Subdirectory to search (relative to infra_dir)
            pattern: Glob pattern (default: *.py)

        Returns:
            List of file information dictionaries
        """
        if directory and not self._is_safe_path(directory):
            raise ValueError(f"Invalid directory path: {directory}")

        target_dir = self.infra_dir / directory if directory else self.infra_dir
        files = []

        try:
            for item in target_dir.rglob(pattern):
                # Skip venv, __pycache__, and hidden directories
                if any(part.startswith(('.', '__pycache__')) or part == 'venv' for part in item.parts):
                    continue

                if item.is_file():
                    try:
                        relative_path = item.relative_to(self.infra_dir)
                        stat_info = item.stat()

                        files.append({
                            "path": str(relative_path).replace('\\', '/'),
                            "name": item.name,
                            "size": stat_info.st_size,
                            "modified": stat_info.st_mtime,
                            "type": "file",
                            "extension": item.suffix,
                        })
                    except (ValueError, OSError) as e:
                        logger.warning(f"Error processing file {item}: {e}")
                        continue

            # Sort by path
            files.sort(key=lambda x: x["path"])
            logger.info(f"Listed {len(files)} files in {target_dir}")

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise

        return files

    async def list_directory_tree(self, directory: str = "") -> Dict[str, any]:
        """
        Get directory tree structure.

        Args:
            directory: Root directory (relative to infra_dir)

        Returns:
            Nested dictionary representing directory tree
        """
        if directory and not self._is_safe_path(directory):
            raise ValueError(f"Invalid directory path: {directory}")

        target_dir = self.infra_dir / directory if directory else self.infra_dir

        def build_tree(path: Path) -> Dict[str, any]:
            """Recursively build directory tree."""
            if not path.is_dir():
                return None

            tree = {
                "name": path.name or str(path),
                "path": str(path.relative_to(self.infra_dir)).replace('\\', '/'),
                "type": "directory",
                "children": [],
            }

            try:
                for item in sorted(path.iterdir()):
                    # Skip venv, __pycache__, hidden files/dirs
                    if item.name.startswith('.') or item.name in ('venv', '__pycache__'):
                        continue

                    if item.is_dir():
                        subtree = build_tree(item)
                        if subtree:
                            tree["children"].append(subtree)
                    elif item.is_file() and item.suffix in ('.py', '.yaml', '.yml', '.json'):
                        tree["children"].append({
                            "name": item.name,
                            "path": str(item.relative_to(self.infra_dir)).replace('\\', '/'),
                            "type": "file",
                            "extension": item.suffix,
                            "size": item.stat().st_size,
                        })
            except PermissionError:
                logger.warning(f"Permission denied reading directory: {path}")

            return tree

        return build_tree(target_dir)

    async def read_file(self, file_path: str) -> str:
        """
        Read file content.

        Args:
            file_path: Path to file (relative to infra_dir)

        Returns:
            File content as string
        """
        if not self._is_safe_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")

        full_path = self.infra_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not full_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            logger.info(f"Read file: {file_path} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    async def write_file(self, file_path: str, content: str, validate: bool = True) -> bool:
        """
        Write content to file.

        Args:
            file_path: Path to file (relative to infra_dir)
            content: Content to write
            validate: Whether to validate Python syntax (default: True)

        Returns:
            True if successful
        """
        if not self._is_safe_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")

        full_path = self.infra_dir / file_path

        # Validate Python syntax if requested and file is .py
        if validate and full_path.suffix == '.py':
            validation_result = await self.validate_python(content)
            if not validation_result["valid"]:
                raise SyntaxError(
                    f"Invalid Python syntax at line {validation_result.get('line', '?')}: "
                    f"{validation_result.get('error', 'Unknown error')}"
                )

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            logger.info(f"Wrote file: {file_path} ({len(content)} bytes)")
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to file (relative to infra_dir)

        Returns:
            True if successful
        """
        if not self._is_safe_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")

        full_path = self.infra_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not full_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            full_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise

    async def validate_python(self, content: str) -> Dict[str, any]:
        """
        Validate Python code syntax.

        Args:
            content: Python code to validate

        Returns:
            Dictionary with validation result
        """
        try:
            ast.parse(content)
            return {"valid": True}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": str(e.msg),
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text,
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
            }

    async def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists.

        Args:
            file_path: Path to file (relative to infra_dir)

        Returns:
            True if file exists
        """
        if not self._is_safe_path(file_path):
            return False

        full_path = self.infra_dir / file_path
        return full_path.exists() and full_path.is_file()


# Global instance
file_service = FileService()
