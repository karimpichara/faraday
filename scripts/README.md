# Database Seeding Scripts

This directory contains scripts to help populate your database with test data for local development.

## seed_database.py

A comprehensive script that creates realistic test data for the Faraday application.

### What it creates:

- **3 Empresas Externas**:

  - Servicios Eléctricos del Norte (SEN)
  - Infraestructura Central SpA (ICS)
  - Telecomunicaciones del Sur (TDS)

- **3 Users** (one per empresa):

  - `supervisor_sen` / `password123`
  - `supervisor_ics` / `password123`
  - `supervisor_tds` / `password123`

- **Multiple Técnicos/Supervisores** per empresa (3-5 each)

- **3-5 Órdenes de Trabajo** per empresa with unique códigos

- **2-6 Comentarios** per orden de trabajo:

  - Some with images from the uploads folder (30% chance)
  - Realistic technical comments
  - Random ticket numbers

- **Historical data** for testing queries and reports

### Usage:

#### Option 1: Using the helper script (recommended)

```bash
# Test environment first
./scripts/run_seeding.sh test

# Run validation and seeding with confirmation
./scripts/run_seeding.sh seed
```

#### Option 2: Direct execution

```bash
# From project root
python scripts/seed_database.py

# Or if executable
./scripts/seed_database.py
```

#### Option 3: Validation only

```bash
# Test if environment is ready for seeding
python scripts/test_seed.py
./scripts/test_seed.py
```

### Requirements:

- Database must be created and migrations applied
- Flask app configuration properly set up
- Images should exist in `uploads/comentarios/` folder

### Safety Features:

- Checks for existing data to avoid duplicates
- Provides detailed logging of what's being created
- Can be run multiple times safely
- Uses transactions for data consistency
- Uses testing images from `uploads/comentarios/testing/` folder

### Customization:

You can modify the script to:

- Add more empresas by editing `empresa_data`
- Change the number of records created
- Add different tipos of comentarios
- Modify the sample technical data

The script is designed to be idempotent - you can run it multiple times without creating duplicate data.

## verify_images.py

A utility script to verify that all comentario images are accessible and properly linked.

### Usage:

```bash
python scripts/verify_images.py
```

This script:

- Checks all comentarios with images in the database
- Verifies that the image files exist and are accessible
- Reports any missing or broken image links
- Shows a summary of accessible vs missing images

Useful for troubleshooting image display issues after seeding or migrations.
