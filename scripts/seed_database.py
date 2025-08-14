#!/usr/bin/env python3
"""
Database seeding script for Faraday project.
This script populates the database with realistic test data for local development.

Usage:
    python scripts/seed_database.py

This script will create:
- 3 Empresas with one user each
- Multiple tecnicos/supervisores for each empresa
- 3-5 ordenes de trabajo per empresa
- Several comentarios per orden de trabajo (with and without photos)
- Required roles and relationships
"""

import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app import create_app
from src.models import db
from src.models.auth.user import Role, User, UserEmpresa, UserRole
from src.models.comentarios import Comentario
from src.models.empresas_externas_toa import EmpresasExternasToa
from src.models.historia_ot_empresas import HistoriaOtEmpresas
from src.models.orden_trabajo import OrdenTrabajo
from src.models.tecnico_supervisor import TecnicoSupervisor


class DatabaseSeeder:
    """Class to handle database seeding operations."""

    def __init__(self, app):
        self.app = app
        self.created_empresas = []
        self.created_users = []
        self.created_tecnicos = []
        self.created_ordenes = []
        self.created_comentarios = []

        # Available images from uploads folder
        self.available_images = [
            "52e9d3414854aa14f1dc8460962e33791c3ad6e04e507441722a72dd964bc7_640.jpg",
            "54e2d4444d56ab14f1dc8460962e33791c3ad6e04e5074417d2d73d3954ac7_640.jpg",
            "54e9d1454a57ab14f1dc8460962e33791c3ad6e04e507440752f72d6914ac3_640.jpg",
            "57e0dc434d55ac14f1dc8460962e33791c3ad6e04e50744172287ad2954ac2_640.jpg",
            "57e2d4474d56aa14f1dc8460962e33791c3ad6e04e5074417d2e72d29f44c5_640.jpg",
            "57e4dc44434faa0df7c5d57bc32f3e7b1d3ac3e45551754c7c287bd596_640.jpg",
            "57e6d0424356a914f1dc8460962e33791c3ad6e04e50744172287edc904fc7_640.jpg",
            "57e6d6434e55ae14f1dc8460962e33791c3ad6e04e5074417c2f7dd5924dc5_640.jpg",
            "5ee2d34b4953b10ff3d8992cc12c30771037dbf85254794e702672dc9044_640.jpg",
            "5fe9d1414d50b10ff3d8992cc12c30771037dbf85254784875287fd7914b_640.jpg",
            "j1.png",
            "manipulation-1875815_640.jpg",
            "tiger-2430625_640.jpg",
        ]

        # Constants for repeated values
        SANDRA_PATRICIA = "Sandra Patricia Rojas"

        # Sample data for creating realistic test records
        self.empresa_data = [
            {
                "nombre": "Servicios Eléctricos del Norte",
                "nombre_toa": "SEN",
                "rut": "96.123.456-7",
            },
            {
                "nombre": "Infraestructura Central SpA",
                "nombre_toa": "ICS",
                "rut": "76.789.012-3",
            },
            {
                "nombre": "Telecomunicaciones del Sur",
                "nombre_toa": "TDS",
                "rut": "99.345.678-9",
            },
        ]

        self.tecnicos_data = [
            # For SEN
            [
                {
                    "nombre": "Juan Carlos Pérez",
                    "rut": "12.345.678-9",
                    "supervisor": "Ana María González",
                },
                {
                    "nombre": "Pedro Antonio López",
                    "rut": "11.234.567-8",
                    "supervisor": "Ana María González",
                },
                {
                    "nombre": "Carlos Eduardo Ramirez",
                    "rut": "13.456.789-0",
                    "supervisor": "Roberto Silva Medina",
                },
                {
                    "nombre": "Miguel Angel Torres",
                    "rut": "14.567.890-1",
                    "supervisor": "Roberto Silva Medina",
                },
            ],
            # For ICS
            [
                {
                    "nombre": "Francisco Javier Morales",
                    "rut": "15.678.901-2",
                    "supervisor": "María Elena Castro",
                },
                {
                    "nombre": "Luis Fernando Herrera",
                    "rut": "16.789.012-3",
                    "supervisor": "María Elena Castro",
                },
                {
                    "nombre": "Jorge Patricio Vega",
                    "rut": "17.890.123-4",
                    "supervisor": SANDRA_PATRICIA,
                },
                {
                    "nombre": "Andrés Felipe Muñoz",
                    "rut": "18.901.234-5",
                    "supervisor": SANDRA_PATRICIA,
                },
                {
                    "nombre": "Ricardo Alejandro Soto",
                    "rut": "19.012.345-6",
                    "supervisor": SANDRA_PATRICIA,
                },
            ],
            # For TDS
            [
                {
                    "nombre": "Daniel Esteban Vargas",
                    "rut": "20.123.456-7",
                    "supervisor": "Carmen Gloria Fuentes",
                },
                {
                    "nombre": "Rodrigo Sebastián Díaz",
                    "rut": "21.234.567-8",
                    "supervisor": "Carmen Gloria Fuentes",
                },
                {
                    "nombre": "Mauricio Ignacio Contreras",
                    "rut": "22.345.678-9",
                    "supervisor": "Patricio Hernán Flores",
                },
            ],
        ]

        self.comentarios_examples = [
            "Trabajo iniciado. Revisando equipamiento en terreno.",
            "Detectado problema en conexión principal. Procediendo con reparación.",
            "Equipo funcionando correctamente después de mantenimiento.",
            "Instalación completada según especificaciones técnicas.",
            "Problema resuelto. Sistema operativo nuevamente.",
            "Revisión de seguridad completada sin observaciones.",
            "Cambio de componente defectuoso realizado exitosamente.",
            "Pruebas de funcionamiento finalizadas satisfactoriamente.",
            "Trabajo suspendido por condiciones climáticas adversas.",
            "Coordenadas verificadas y marcadas correctamente.",
            "Material adicional requerido para completar instalación.",
            "Conexión establecida y probada exitosamente.",
            "Mantenimiento preventivo realizado según cronograma.",
            "Anomalía detectada en sensor, requiere reemplazo.",
            "Trabajo finalizado dentro del tiempo estimado.",
            "Documentación técnica actualizada correctamente.",
            "Sistema de monitoreo activado y funcionando.",
            "Calibración de equipos completada exitosamente.",
        ]

    def run(self):
        """Execute the complete seeding process."""
        with self.app.app_context():
            print("🌱 Iniciando proceso de seeding de la base de datos...")

            try:
                # Clear existing test data (optional - comment out if you want to keep existing data)
                # self.clear_test_data()

                # Create required roles first
                self.create_roles()

                # Create empresas
                self.create_empresas()

                # Create users for each empresa
                self.create_users()

                # Create tecnicos/supervisores
                self.create_tecnicos_supervisores()

                # Create ordenes de trabajo
                self.create_ordenes_trabajo()

                # Create comentarios
                self.create_comentarios()

                # Create some historical data
                self.create_historia_data()

                self.print_summary()
                print("✅ Seeding completado exitosamente!")

            except Exception as e:
                print(f"❌ Error durante el seeding: {str(e)}")
                db.session.rollback()
                raise

    def clear_test_data(self):
        """Clear existing test data (use with caution)."""
        print("🧹 Limpiando datos de prueba existentes...")

        # Delete in reverse order of dependencies
        Comentario.query.delete()
        OrdenTrabajo.query.delete()
        TecnicoSupervisor.query.delete()
        UserEmpresa.query.delete()
        UserRole.query.delete()
        # Don't delete users entirely as there might be a 'dev' user
        User.query.filter(User.username != "dev").delete()
        EmpresasExternasToa.query.delete()
        HistoriaOtEmpresas.query.delete()

        db.session.commit()
        print("✅ Datos de prueba eliminados")

    def create_roles(self):
        """Create required user roles."""
        print("👥 Creando roles de usuario...")

        roles = ["supervisor", "admin", "tecnico"]

        for role_name in roles:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                role = Role(name=role_name)
                db.session.add(role)
                print(f"   ✓ Rol creado: {role_name}")
            else:
                print(f"   ⚠ Rol ya existe: {role_name}")

        db.session.commit()

    def create_empresas(self):
        """Create test empresas."""
        print("🏢 Creando empresas...")

        for empresa_info in self.empresa_data:
            # Check if empresa already exists
            existing = EmpresasExternasToa.query.filter_by(
                rut=empresa_info["rut"]
            ).first()
            if existing:
                print(f"   ⚠ Empresa ya existe: {empresa_info['nombre']}")
                self.created_empresas.append(existing)
                continue

            empresa = EmpresasExternasToa(
                nombre=empresa_info["nombre"],
                nombre_toa=empresa_info["nombre_toa"],
                rut=empresa_info["rut"],
            )
            db.session.add(empresa)
            self.created_empresas.append(empresa)
            print(f"   ✓ Empresa creada: {empresa_info['nombre']}")

        db.session.commit()

    def create_users(self):
        """Create one user per empresa with supervisor role."""
        print("👤 Creando usuarios...")

        supervisor_role = Role.query.filter_by(name="supervisor").first()
        if not supervisor_role:
            raise ValueError("El rol 'supervisor' no existe")

        usernames = ["supervisor_sen", "supervisor_ics", "supervisor_tds"]

        for i, empresa in enumerate(self.created_empresas):
            username = usernames[i]

            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"   ⚠ Usuario ya existe: {username}")
                self.created_users.append(existing_user)
                continue

            # Create user
            user = User(username=username, password="password123")
            db.session.add(user)
            db.session.flush()  # Get the user ID

            # Assign supervisor role
            user_role = UserRole(user_id=user.id, role_id=supervisor_role.id)
            db.session.add(user_role)

            # Assign to empresa
            user_empresa = UserEmpresa(user_id=user.id, empresa_id=empresa.id)
            db.session.add(user_empresa)

            self.created_users.append(user)
            print(f"   ✓ Usuario creado: {username} (empresa: {empresa.nombre})")

        db.session.commit()

    def create_tecnicos_supervisores(self):
        """Create tecnicos and supervisores for each empresa."""
        print("🔧 Creando técnicos y supervisores...")

        for i, empresa in enumerate(self.created_empresas):
            tecnicos_empresa = self.tecnicos_data[i]

            for tecnico_info in tecnicos_empresa:
                # Check if tecnico already exists
                existing = TecnicoSupervisor.query.filter_by(
                    rut_tecnico=tecnico_info["rut"]
                ).first()
                if existing:
                    print(f"   ⚠ Técnico ya existe: {tecnico_info['nombre']}")
                    self.created_tecnicos.append(existing)
                    continue

                tecnico = TecnicoSupervisor(
                    nombre_tecnico=tecnico_info["nombre"],
                    rut_tecnico=tecnico_info["rut"],
                    nombre_supervisor=tecnico_info["supervisor"],
                    id_empresa=empresa.id,
                )
                db.session.add(tecnico)
                self.created_tecnicos.append(tecnico)
                print(
                    f"   ✓ Técnico creado: {tecnico_info['nombre']} (supervisor: {tecnico_info['supervisor']})"
                )

        db.session.commit()

    def create_ordenes_trabajo(self):
        """Create ordenes de trabajo for each empresa."""
        print("📋 Creando órdenes de trabajo...")

        for empresa in self.created_empresas:
            # Create 3-5 ordenes per empresa
            num_ordenes = random.randint(3, 5)

            for _ in range(num_ordenes):
                # Generate unique codigo
                codigo = f"{empresa.nombre_toa}-{datetime.now().year}-{random.randint(1000, 9999)}"

                # Check if orden already exists
                existing = OrdenTrabajo.query.filter_by(codigo=codigo).first()
                if existing:
                    print(f"   ⚠ Orden ya existe: {codigo}")
                    self.created_ordenes.append(existing)
                    continue

                orden = OrdenTrabajo(codigo=codigo, id_empresa=empresa.id)
                db.session.add(orden)
                self.created_ordenes.append(orden)
                print(f"   ✓ Orden creada: {codigo} (empresa: {empresa.nombre})")

        db.session.commit()

    def create_comentarios(self):
        """Create comentarios for each orden de trabajo."""
        print("💬 Creando comentarios...")

        for orden in self.created_ordenes:
            # Get empresa and user for this orden
            empresa = next(
                emp for emp in self.created_empresas if emp.id == orden.id_empresa
            )
            user = next(
                usr
                for usr in self.created_users
                if any(ue.id == empresa.id for ue in usr.empresas)
            )

            # Create 2-6 comentarios per orden
            num_comentarios = random.randint(2, 6)

            for _ in range(num_comentarios):
                comentario_text = random.choice(self.comentarios_examples)
                ticket_num = f"TK-{random.randint(10000, 99999)}"

                # 30% chance of having an image
                imagen_path = None
                imagen_original_name = None
                if random.random() < 0.3 and self.available_images:
                    image_file = random.choice(self.available_images)
                    # Use proper path joining instead of string formatting
                    from src.constants import get_upload_path
                    imagen_path = get_upload_path("comentarios", "testing", image_file)
                    imagen_original_name = image_file

                comentario = Comentario(
                    comentario=comentario_text,
                    num_ticket=ticket_num,
                    imagen_path=imagen_path,
                    imagen_original_name=imagen_original_name,
                    id_orden_trabajo=orden.id,
                    id_usuario=user.id,
                )

                # Set random creation time in the past (last 30 days)
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                comentario.created_at = datetime.now() - timedelta(
                    days=days_ago, hours=hours_ago
                )
                comentario.updated_at = comentario.created_at

                db.session.add(comentario)
                self.created_comentarios.append(comentario)

                image_info = (
                    f" (con imagen: {imagen_original_name})" if imagen_path else ""
                )
                print(
                    f"   ✓ Comentario creado: {ticket_num} - {comentario_text[:50]}...{image_info}"
                )

        db.session.commit()

    def create_historia_data(self):
        """Create some sample historical data."""
        print("📊 Creando datos históricos...")

        zonas = ["Norte", "Centro", "Sur", "Metropolitana"]
        estados = ["Iniciado", "En Progreso", "Completado", "Pendiente"]
        tipos_actividad = ["Instalación", "Mantenimiento", "Reparación", "Inspección"]

        for empresa in self.created_empresas:
            # Create 2-3 historical records per empresa
            num_registros = random.randint(2, 3)

            for _ in range(num_registros):
                # Get a random tecnico from this empresa
                tecnicos_empresa = [
                    t for t in self.created_tecnicos if t.id_empresa == empresa.id
                ]
                if not tecnicos_empresa:
                    continue

                tecnico = random.choice(tecnicos_empresa)

                # Random date in the last 60 days
                fecha_base = datetime.now() - timedelta(days=random.randint(1, 60))
                fecha_str = fecha_base.strftime("%Y-%m-%d")

                historia = HistoriaOtEmpresas(
                    zona=random.choice(zonas),
                    orden_de_trabajo=f"OT-{random.randint(100000, 999999)}",
                    empresa=empresa.nombre,
                    tecnico=tecnico.nombre_tecnico,
                    coord_x=str(
                        round(random.uniform(-74, -66), 6)
                    ),  # Chile longitude range
                    coord_y=str(
                        round(random.uniform(-56, -17), 6)
                    ),  # Chile latitude range
                    duracion=f"{random.randint(30, 480)} minutos",
                    estado=random.choice(estados),
                    fecha=fecha_str,
                    flag_consulta_vecino=random.choice(["Sí", "No"]),
                    flag_estado_aprovision=random.choice(
                        ["Aprobado", "Pendiente", "Rechazado"]
                    ),
                    flag_fallas_masivas=random.choice(["Sí", "No"]),
                    flag_materiales=random.choice(["Disponible", "Faltante"]),
                    flag_niveles=random.choice(["Normal", "Crítico", "Alerta"]),
                    hora_flag_estado_aprovision=fecha_base.strftime("%H:%M"),
                    hora_flag_fallas_masivas=fecha_base.strftime("%H:%M"),
                    hora_flag_materiales=fecha_base.strftime("%H:%M"),
                    hora_flag_niveles=fecha_base.strftime("%H:%M"),
                    inicio=fecha_base.strftime("%H:%M"),
                    intervencion_neutra=random.choice(["Sí", "No"]),
                    notas_consulta_vecino=(
                        "Consulta realizada sin observaciones"
                        if random.random() > 0.5
                        else None
                    ),
                    notas_consulta_vecino_ultimo=(
                        "Última consulta OK" if random.random() > 0.5 else None
                    ),
                    qr_drop=f"QR-{random.randint(1000000, 9999999)}",
                    rut_tecnico=tecnico.rut_tecnico,
                    tipo_red_producto=random.choice(
                        ["Fibra Óptica", "Cobre", "Coaxial", "Inalámbrico"]
                    ),
                    hora_ultima_vecino=(
                        fecha_base.strftime("%H:%M") if random.random() > 0.5 else None
                    ),
                    hora_qr=fecha_base.strftime("%H:%M"),
                    tipo_actividad=random.choice(tipos_actividad),
                    zona_de_trabajo=f"Zona {random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1, 99)}",
                    pasos="1. Revisión inicial\n2. Diagnóstico\n3. Ejecución\n4. Pruebas\n5. Cierre",
                    pelo=random.choice(["Corto", "Largo", "Medio", "Sin especificar"]),
                )

                db.session.add(historia)
                print(
                    f"   ✓ Registro histórico creado: OT-{historia.orden_de_trabajo} (empresa: {empresa.nombre})"
                )

        db.session.commit()

    def print_summary(self):
        """Print a summary of created records."""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DEL SEEDING")
        print("=" * 60)
        print(f"✅ Empresas creadas: {len(self.created_empresas)}")
        print(f"✅ Usuarios creados: {len(self.created_users)}")
        print(f"✅ Técnicos/Supervisores creados: {len(self.created_tecnicos)}")
        print(f"✅ Órdenes de trabajo creadas: {len(self.created_ordenes)}")
        print(f"✅ Comentarios creados: {len(self.created_comentarios)}")

        print("\n📋 DETALLES DE EMPRESAS:")
        for empresa in self.created_empresas:
            user = next(
                (
                    u
                    for u in self.created_users
                    if any(ue.id == empresa.id for ue in u.empresas)
                ),
                None,
            )
            user_info = f" (usuario: {user.username})" if user else ""
            print(f"  • {empresa.nombre} ({empresa.nombre_toa}){user_info}")

        print("\n🔑 CREDENCIALES DE ACCESO:")
        for user in self.created_users:
            print(f"  • Usuario: {user.username} | Contraseña: password123")

        print("\n📸 IMÁGENES DISPONIBLES:")
        images_with_comments = len(
            [c for c in self.created_comentarios if c.imagen_path]
        )
        print(f"  • Comentarios con imágenes: {images_with_comments}")
        print(
            f"  • Imágenes disponibles en uploads/comentarios/: {len(self.available_images)}"
        )


def main():
    """Main function to run the seeding script."""
    print("🌱 Faraday Database Seeder")
    print("=" * 50)

    # Create Flask app
    app = create_app()

    # Run seeding
    seeder = DatabaseSeeder(app)
    seeder.run()


if __name__ == "__main__":
    main()
