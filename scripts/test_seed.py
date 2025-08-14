#!/usr/bin/env python3
"""
Test script to validate the seeding functionality without actually seeding the database.
This script performs dry-run checks to ensure the seeding script would work correctly.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app import create_app
from src.models import db
from src.models.auth.user import Role


def test_database_connection():
    """Test database connection."""
    print("🔗 Probando conexión a la base de datos...")
    try:
        app = create_app()
        with app.app_context():
            # Simple query to test connection
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            if result:
                print("✅ Conexión a la base de datos exitosa")
                return True
            else:
                print("❌ Error en la conexión a la base de datos")
                return False
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False


def test_tables_exist():
    """Test that required tables exist."""
    print("📋 Verificando que las tablas existen...")
    
    required_tables = [
        "empresas_externas_toa",
        "users", 
        "roles",
        "user_roles",
        "user_empresas",
        "tecnicos_supervisores",
        "ordenes_trabajo",
        "comentarios",
        "historia_ot_empresas"
    ]
    
    try:
        app = create_app()
        with app.app_context():
            # Get all table names
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    print(f"   ✅ Tabla encontrada: {table}")
                else:
                    print(f"   ❌ Tabla faltante: {table}")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n⚠️  Faltan las siguientes tablas: {', '.join(missing_tables)}")
                print("   Ejecuta las migraciones con: flask db upgrade")
                return False
            else:
                print("✅ Todas las tablas requeridas existen")
                return True
                
    except Exception as e:
        print(f"❌ Error verificando tablas: {str(e)}")
        return False


def test_uploads_folder():
    """Test that uploads folder and images exist."""
    print("📁 Verificando carpeta de uploads...")
    
    uploads_path = project_root / "uploads" / "comentarios"
    
    if not uploads_path.exists():
        print(f"❌ Carpeta de uploads no existe: {uploads_path}")
        return False
    
    # Check for images
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    images = [f for f in uploads_path.iterdir() 
             if f.is_file() and f.suffix.lower() in image_extensions]
    
    if images:
        print(f"✅ Carpeta de uploads encontrada con {len(images)} imágenes")
        print(f"   Ruta: {uploads_path}")
        # Show first few images as examples
        for i, img in enumerate(images[:3]):
            print(f"   • {img.name}")
        if len(images) > 3:
            print(f"   ... y {len(images) - 3} más")
        return True
    else:
        print(f"⚠️  Carpeta de uploads existe pero no hay imágenes")
        print(f"   Ruta: {uploads_path}")
        print("   El seeding funcionará pero los comentarios no tendrán imágenes")
        return True


def test_required_roles():
    """Test that required roles exist or can be created."""
    print("👥 Verificando roles...")
    
    try:
        app = create_app()
        with app.app_context():
            supervisor_role = Role.query.filter_by(name="supervisor").first()
            if supervisor_role:
                print("✅ Rol 'supervisor' ya existe")
            else:
                print("⚠️  Rol 'supervisor' no existe, será creado durante el seeding")
            
            return True
    except Exception as e:
        print(f"❌ Error verificando roles: {str(e)}")
        return False


def test_import_dependencies():
    """Test that all required imports work."""
    print("📦 Verificando dependencias de Python...")
    
    try:
        # Test all the imports the seeding script uses
        from src.models.auth.user import Role, User, UserEmpresa, UserRole
        from src.models.comentarios import Comentario
        from src.models.empresas_externas_toa import EmpresasExternasToa
        from src.models.historia_ot_empresas import HistoriaOtEmpresas
        from src.models.orden_trabajo import OrdenTrabajo
        from src.models.tecnico_supervisor import TecnicoSupervisor
        
        print("✅ Todas las dependencias están disponibles")
        return True
    except ImportError as e:
        print(f"❌ Error importando dependencias: {str(e)}")
        return False


def run_all_tests():
    """Run all validation tests."""
    print("🧪 VALIDACIÓN DE ENTORNO PARA SEEDING")
    print("=" * 50)
    
    tests = [
        ("Conexión a base de datos", test_database_connection),
        ("Tablas de base de datos", test_tables_exist),
        ("Carpeta de uploads", test_uploads_folder),
        ("Roles requeridos", test_required_roles),
        ("Dependencias Python", test_import_dependencies),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ El entorno está listo para ejecutar el seeding")
        print("\nPara ejecutar el seeding:")
        print("   python scripts/seed_database.py")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print("❌ Corrige los errores antes de ejecutar el seeding")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
