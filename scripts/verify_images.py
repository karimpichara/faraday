#!/usr/bin/env python3
"""
Script to verify that all comentario images can be found and accessed.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app import create_app
from src.models.comentarios import Comentario
from src.constants import ROOT_PATH


def verify_images():
    """Verify all comentario images are accessible."""
    app = create_app()
    
    with app.app_context():
        print("🔍 Verifying comentario images...")
        print(f"📁 ROOT_PATH: {ROOT_PATH}")
        
        # Get all comentarios with images
        comentarios_with_images = Comentario.query.filter(
            Comentario.imagen_path.isnot(None)
        ).all()
        
        if not comentarios_with_images:
            print("ℹ️  No comentarios with images found")
            return
        
        print(f"📝 Found {len(comentarios_with_images)} comentarios with images")
        
        accessible_count = 0
        missing_count = 0
        
        for comentario in comentarios_with_images:
            imagen_path = comentario.imagen_path
            
            # Simulate the same logic as the application route
            if os.path.isabs(imagen_path):
                full_image_path = imagen_path
            else:
                full_image_path = os.path.join(ROOT_PATH, imagen_path)
            
            if os.path.exists(full_image_path):
                accessible_count += 1
                print(f"   ✅ {comentario.id}: {comentario.imagen_original_name}")
            else:
                missing_count += 1
                print(f"   ❌ {comentario.id}: MISSING - {imagen_path}")
                print(f"       Expected at: {full_image_path}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Accessible images: {accessible_count}")
        print(f"   ❌ Missing images: {missing_count}")
        
        if missing_count == 0:
            print("🎉 All images are accessible!")
        else:
            print("⚠️  Some images are missing - check paths and files")


if __name__ == "__main__":
    verify_images()
