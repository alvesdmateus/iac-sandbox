"""File management API endpoints."""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models.file import (
    FileInfo,
    DirectoryTree,
    FileContent,
    UpdateFileRequest,
    CreateFileRequest,
    ValidatePythonRequest,
    ValidationResult,
)
from ..services.file_service import file_service


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/files/infra", response_model=List[FileInfo])
async def list_files(
    directory: str = Query("", description="Subdirectory to list"),
    pattern: str = Query("*.py", description="File pattern to match")
):
    """List all files in infrastructure directory."""
    try:
        files = await file_service.list_files(directory=directory, pattern=pattern)
        return files
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/infra/tree", response_model=DirectoryTree)
async def get_directory_tree(
    directory: str = Query("", description="Root directory")
):
    """Get directory tree structure."""
    try:
        tree = await file_service.list_directory_tree(directory=directory)
        return tree
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting directory tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/infra/{file_path:path}", response_model=FileContent)
async def read_file(file_path: str):
    """Read file content."""
    try:
        content = await file_service.read_file(file_path)
        return FileContent(
            path=file_path,
            content=content,
            size=len(content),
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/files/infra/{file_path:path}")
async def update_file(file_path: str, request: UpdateFileRequest):
    """Update file content."""
    try:
        success = await file_service.write_file(
            file_path=file_path,
            content=request.content,
            validate=request.validate,
        )
        return JSONResponse(
            content={
                "message": f"File {file_path} updated successfully",
                "size": len(request.content),
            }
        )
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Python syntax: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/infra", status_code=201)
async def create_file(request: CreateFileRequest):
    """Create a new file."""
    try:
        # Check if file already exists
        if await file_service.file_exists(request.path):
            raise HTTPException(
                status_code=409,
                detail=f"File already exists: {request.path}"
            )

        success = await file_service.write_file(
            file_path=request.path,
            content=request.content,
            validate=request.validate,
        )

        return JSONResponse(
            content={
                "message": f"File {request.path} created successfully",
                "path": request.path,
                "size": len(request.content),
            },
            status_code=201,
        )
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Python syntax: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating file {request.path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/infra/{file_path:path}")
async def delete_file(file_path: str):
    """Delete a file."""
    try:
        success = await file_service.delete_file(file_path)
        return JSONResponse(
            content={"message": f"File {file_path} deleted successfully"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/infra/validate", response_model=ValidationResult)
async def validate_python(request: ValidatePythonRequest):
    """Validate Python code syntax."""
    try:
        result = await file_service.validate_python(request.content)
        return ValidationResult(**result)
    except Exception as e:
        logger.error(f"Error validating Python code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
