"""
Image utility functions for serving and handling images.
"""

import os
from io import BytesIO

from flask import send_file
from PIL import Image


def serve_default_placeholder_image():
    """
    Serve a default placeholder image when no image is available.
    Returns the company logo as a fallback, or creates a minimal transparent PNG.

    Returns:
        Flask response with image file
    """
    try:
        # Use company logo as placeholder
        logo_path = os.path.join("src", "app", "static", "img", "logo_cre_blanco.png")
        if os.path.exists(logo_path):
            return send_file(logo_path)
    except Exception:
        pass

    # If logo doesn't exist, create a minimal 1x1 transparent PNG in memory
    # Create 1x1 transparent image
    img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=False,
        download_name="placeholder.png",
    )
