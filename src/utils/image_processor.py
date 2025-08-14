"""
Image processing utilities for comment attachments.
Handles image compression, validation, and storage.
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps
from werkzeug.datastructures import FileStorage

from src.constants import COMENTARIOS_UPLOAD_PATH


class ImageProcessor:
    """Handles image processing for comment attachments."""

    # Supported image formats
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

    # Image constraints
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    COMPRESSION_QUALITY = 85

    # Storage configuration
    UPLOAD_FOLDER = COMENTARIOS_UPLOAD_PATH

    def __init__(self, upload_folder: str = None):
        """Initialize the image processor."""
        self.upload_folder = upload_folder or self.UPLOAD_FOLDER
        self._ensure_upload_directory()

    def _ensure_upload_directory(self) -> None:
        """Ensure the upload directory exists."""
        Path(self.upload_folder).mkdir(parents=True, exist_ok=True)

    def is_allowed_file(self, filename: str) -> bool:
        """Check if the file extension is allowed."""
        if not filename:
            return False
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    def validate_file(self, file: FileStorage) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No se proporcionó archivo"

        if not self.is_allowed_file(file.filename):
            allowed = ", ".join(self.ALLOWED_EXTENSIONS)
            return False, f"Formato no permitido. Use: {allowed}"

        # Check file size (file.content_length might not be available)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE // (1024 * 1024)
            return False, f"Archivo muy grande. Máximo: {max_mb}MB"

        # Try to open as image to validate format
        try:
            with Image.open(file.stream) as img:
                img.verify()
            file.seek(0)  # Reset stream position
            return True, None
        except Exception:
            return False, "Archivo no es una imagen válida"

    def compress_image(self, image: Image.Image) -> Image.Image:
        """
        Compress and resize image if needed.

        Args:
            image: PIL Image object

        Returns:
            Compressed PIL Image object
        """
        # Convert to RGB if necessary (handles RGBA, P mode images)
        if image.mode in ("RGBA", "P", "LA"):
            # Create white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image, mask=image.split()[-1] if image.mode == "RGBA" else None
            )
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Auto-orient image based on EXIF data
        image = ImageOps.exif_transpose(image)

        # Resize if too large
        if image.width > self.MAX_WIDTH or image.height > self.MAX_HEIGHT:
            image.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT), Image.Resampling.LANCZOS)

        return image

    def generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename for storage."""
        ext = original_filename.rsplit(".", 1)[1].lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{ext}"

    def save_image(
        self, file: FileStorage
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Process and save uploaded image.

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success, file_path, error_message)
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            return False, None, error_message

        try:
            # Generate unique filename
            filename = self.generate_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)

            # Open and process image
            with Image.open(file.stream) as img:
                processed_img = self.compress_image(img)

                # Save compressed image
                processed_img.save(
                    file_path,
                    format="JPEG",
                    quality=self.COMPRESSION_QUALITY,
                    optimize=True,
                )

            return True, file_path, None

        except Exception as e:
            return False, None, f"Error al procesar imagen: {str(e)}"

    def delete_image(self, file_path: str) -> bool:
        """
        Delete image file from storage.

        Args:
            file_path: Path to the image file

        Returns:
            bool: True if deleted successfully
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True
            return True  # File doesn't exist, consider as deleted
        except Exception:
            return False

    def get_image_info(self, file_path: str) -> Optional[dict]:
        """
        Get image information.

        Args:
            file_path: Path to the image file

        Returns:
            Dict with image info or None if error
        """
        try:
            if not os.path.exists(file_path):
                return None

            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": os.path.getsize(file_path),
                }
        except Exception:
            return None
