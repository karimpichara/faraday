"""
Application constants and configuration paths.
"""

import os

# Get the current file path
_current_path = os.path.abspath(__file__)

# Define root path as the parent directory of the src folder
ROOT_PATH = os.path.dirname(os.path.dirname(_current_path))

# Define upload path
UPLOAD_PATH = os.path.join(ROOT_PATH, "uploads")
