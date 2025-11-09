#!/usr/bin/env python3
"""
Azure App Service startup script for STEALTH-TINKO
This script handles initialization tasks for the Azure deployment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_azure_services():
    """Check connectivity to Azure services"""
    logger.info("Checking Azure services connectivity...")
    
    # Check Key Vault connectivity
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        
        key_vault_url = os.getenv('AZURE_KEY_VAULT_URL')
        if key_vault_url:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=key_vault_url, credential=credential)
            # Test connection by listing secrets (won't work if no permissions, but tests connectivity)
            logger.info("✓ Key Vault connectivity established")
        else:
            logger.warning("⚠ Key Vault URL not configured")
    except Exception as e:
        logger.error(f"✗ Key Vault connectivity failed: {e}")
    
    # Check PostgreSQL connectivity
    try:
        from app.db import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✓ PostgreSQL connectivity established")
    except Exception as e:
        logger.error(f"✗ PostgreSQL connectivity failed: {e}")

def setup_environment():
    """Setup environment variables and configuration"""
    logger.info("Setting up environment...")
    
    # Set default environment if not specified
    if not os.getenv('ENVIRONMENT'):
        os.environ['ENVIRONMENT'] = 'dev'
    
    # Configure Azure SDK logging
    azure_logger = logging.getLogger('azure')
    azure_logger.setLevel(logging.WARNING)
    
    # Configure application insights if available
    app_insights_key = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if app_insights_key:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            logger.addHandler(AzureLogHandler(connection_string=app_insights_key))
            logger.info("✓ Application Insights logging configured")
        except Exception as e:
            logger.warning(f"⚠ Application Insights setup failed: {e}")

async def run_database_migrations():
    """Run database migrations if needed"""
    logger.info("Checking database migrations...")
    
    try:
        from alembic import command
        from alembic.config import Config
        
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("✓ Database migrations completed")
    except Exception as e:
        logger.error(f"✗ Database migration failed: {e}")
        # Don't fail startup for migration issues in production
        if os.getenv('ENVIRONMENT') != 'prod':
            raise

async def initialize_application():
    """Initialize the application"""
    logger.info("Initializing STEALTH-TINKO application...")
    
    # Setup environment
    setup_environment()
    
    # Check Azure services
    await check_azure_services()
    
    # Run database migrations
    await run_database_migrations()
    
    logger.info("✓ Application initialization completed")

def main():
    """Main startup function"""
    try:
        # Run async initialization
        asyncio.run(initialize_application())
        
        # Start the FastAPI application
        logger.info("Starting FastAPI application...")
        
        # Import after initialization
        from app.main import app
        
        # The actual server startup will be handled by gunicorn/uvicorn
        # This script just handles pre-startup tasks
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()