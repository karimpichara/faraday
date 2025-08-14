"""
Application constants and configuration paths.
"""

import os

# Get the current file path (this file's directory)
_current_path = os.path.abspath(os.path.dirname(__file__))

# Define root path as the parent directory of the src folder
ROOT_PATH = os.path.dirname(_current_path)

# Define upload paths using proper path joining
UPLOAD_PATH = os.path.join(ROOT_PATH, "uploads")
COMENTARIOS_UPLOAD_PATH = os.path.join(UPLOAD_PATH, "comentarios")


def get_upload_path(*subdirs):
    """
    Get absolute upload path for any subdirectory.

    Args:
        *subdirs: Variable number of subdirectory names

    Returns:
        str: Absolute path to the upload subdirectory

    Example:
        get_upload_path("comentarios", "testing") -> "/path/to/project/uploads/comentarios/testing"
    """
    return os.path.join(UPLOAD_PATH, *subdirs)


def ensure_upload_directory(path):
    """
    Ensure that an upload directory exists.

    Args:
        path: Path to create if it doesn't exist
    """
    os.makedirs(path, exist_ok=True)
