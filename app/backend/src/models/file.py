"""Pydantic models for file operations."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Information about a file."""
    path: str = Field(description="Relative path to file")
    name: str = Field(description="File name")
    size: int = Field(description="File size in bytes")
    modified: float = Field(description="Last modified timestamp")
    type: str = Field(default="file", description="Type: file or directory")
    extension: str = Field(description="File extension")


class DirectoryTree(BaseModel):
    """Directory tree structure."""
    name: str = Field(description="Directory/file name")
    path: str = Field(description="Relative path")
    type: str = Field(description="Type: file or directory")
    extension: Optional[str] = Field(None, description="File extension if file")
    size: Optional[int] = Field(None, description="File size if file")
    children: List['DirectoryTree'] = Field(default_factory=list, description="Child nodes")


class FileContent(BaseModel):
    """File content response."""
    path: str = Field(description="File path")
    content: str = Field(description="File content")
    size: int = Field(description="Content size in bytes")


class UpdateFileRequest(BaseModel):
    """Request to update a file."""
    content: str = Field(description="New file content")
    validate: bool = Field(default=True, description="Validate Python syntax")


class CreateFileRequest(BaseModel):
    """Request to create a new file."""
    path: str = Field(description="File path (relative to infra dir)")
    content: str = Field(description="File content")
    validate: bool = Field(default=True, description="Validate Python syntax if .py file")


class ValidatePythonRequest(BaseModel):
    """Request to validate Python code."""
    content: str = Field(description="Python code to validate")


class ValidationResult(BaseModel):
    """Python validation result."""
    valid: bool = Field(description="Whether code is valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    line: Optional[int] = Field(None, description="Error line number")
    offset: Optional[int] = Field(None, description="Error column offset")
    text: Optional[str] = Field(None, description="Error line text")


# Update forward references
DirectoryTree.model_rebuild()
