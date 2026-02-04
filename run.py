#!/usr/bin/env python3
"""
UI Toolkit - Application Entry Point

This script starts the UI Toolkit web application.
It checks for required environment variables and starts the FastAPI server.
"""
import os
import sys
from pathlib import Path

# Check if .env file exists
env_file = Path(__file__).parent / ".env"
if not env_file.exists():
    print("=" * 70)
    print("ERROR: .env file not found!")
    print("=" * 70)
    print()
    print("Please create a .env file in the project root directory.")
    print("You can copy .env.example as a starting point:")
    print()
    print("  cp .env.example .env")
    print()
    print("Then edit .env and set the required values:")
    print("  - ENCRYPTION_KEY (required)")
    print("  - UniFi controller settings (optional, can configure via web UI)")
    print()
    print("=" * 70)
    sys.exit(1)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(env_file)
except ImportError:
    print("WARNING: python-dotenv not installed, .env file will not be loaded")
    print("Install it with: pip install python-dotenv")

# Check for required environment variables
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    print("=" * 70)
    print("ERROR: ENCRYPTION_KEY not set in .env file!")
    print("=" * 70)
    print()
    print("The ENCRYPTION_KEY is required to encrypt sensitive data.")
    print("Generate a new key with:")
    print()
    print("  python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    print()
    print("Then add it to your .env file:")
    print()
    print("  ENCRYPTION_KEY=your_generated_key_here")
    print()
    print("=" * 70)
    sys.exit(1)

# Run database migrations before starting the app
# This runs in a normal synchronous context, avoiding any async/uvicorn complications
def run_migrations():
    """Run Alembic migrations before uvicorn starts."""
    try:
        from alembic.config import Config
        from alembic import command

        print("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully")

    except Exception as e:
        error_msg = str(e).lower()

        # Check for common schema sync issues
        schema_sync_errors = [
            "already exists",
            "duplicate column",
            "table already exists",
            "unique constraint failed",
        ]

        is_schema_sync_issue = any(err in error_msg for err in schema_sync_errors)

        if is_schema_sync_issue:
            print(f"Migration detected schema sync issue: {e}")
            print("Attempting to synchronize migration history...")

            try:
                from alembic.config import Config
                from alembic import command

                alembic_cfg = Config("alembic.ini")
                command.stamp(alembic_cfg, "head")
                print("Migration history synchronized with current schema")
            except Exception as stamp_error:
                print(f"Failed to synchronize migration history: {stamp_error}")
        else:
            print(f"Migration warning: {e}")
            print("The application will continue, but some features may not work correctly.")


# Start the application
if __name__ == "__main__":
    import uvicorn
    from shared.config import get_settings
    from app import __version__ as app_version
    from tools.wifi_stalker import __version__ as stalker_version
    from tools.threat_watch import __version__ as threat_watch_version
    from tools.network_pulse import __version__ as pulse_version

    # Run migrations FIRST, before any uvicorn/async stuff
    run_migrations()

    settings = get_settings()

    print("=" * 70)
    print("Starting UI Toolkit...")
    print("=" * 70)
    print()
    print(f"Version: {app_version}")
    print(f"Log Level: {settings.log_level}")
    print(f"Database: {settings.database_url}")
    print()

    # Display deployment mode
    deployment_type = settings.deployment_type.upper()
    if deployment_type == "PRODUCTION":
        print(f"Deployment: PRODUCTION (authentication enabled)")
        if settings.domain:
            print(f"Domain: {settings.domain}")
    else:
        print(f"Deployment: LOCAL (authentication disabled)")
    print()

    print("Available tools:")
    print(f"  - Wi-Fi Stalker v{stalker_version}")
    print(f"  - Threat Watch v{threat_watch_version}")
    print(f"  - Network Pulse v{pulse_version}")
    print()

    if deployment_type == "PRODUCTION":
        print("Access via your configured domain with HTTPS")
    else:
        print(f"Access the dashboard at: http://localhost:{settings.app_port}")
        print(f"Wi-Fi Stalker at: http://localhost:{settings.app_port}/stalker/")
        print(f"Threat Watch at: http://localhost:{settings.app_port}/threats/")
        print(f"Network Pulse at: http://localhost:{settings.app_port}/pulse/")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()

    # Configure logging level
    log_level = settings.log_level.lower()

    # Start uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=False,  # Set to True for development
        log_level=log_level,
        access_log=True
    )
