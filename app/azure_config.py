"""
Azure-specific configuration for STEALTH-TINKO
Handles Azure Key Vault, Storage, and Communication Services integration
"""

import os
import logging
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from azure.communication.email import EmailClient

logger = logging.getLogger(__name__)

class AzureConfig:
    """Azure services configuration and client management"""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self._key_vault_client: Optional[SecretClient] = None
        self._blob_client: Optional[BlobServiceClient] = None
        self._email_client: Optional[EmailClient] = None
        
    @property
    def key_vault_client(self) -> Optional[SecretClient]:
        """Get Key Vault client (lazy loading)"""
        if not self._key_vault_client:
            key_vault_url = os.getenv('AZURE_KEY_VAULT_URL')
            if key_vault_url:
                try:
                    self._key_vault_client = SecretClient(
                        vault_url=key_vault_url,
                        credential=self.credential
                    )
                    logger.info("Key Vault client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Key Vault client: {e}")
        return self._key_vault_client
    
    @property
    def blob_client(self) -> Optional[BlobServiceClient]:
        """Get Blob Storage client (lazy loading)"""
        if not self._blob_client:
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if connection_string:
                try:
                    self._blob_client = BlobServiceClient.from_connection_string(
                        connection_string
                    )
                    logger.info("Blob Storage client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Blob Storage client: {e}")
        return self._blob_client
    
    @property
    def email_client(self) -> Optional[EmailClient]:
        """Get Communication Services Email client (lazy loading)"""
        if not self._email_client:
            connection_string = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
            if connection_string:
                try:
                    self._email_client = EmailClient.from_connection_string(
                        connection_string
                    )
                    logger.info("Communication Services Email client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Email client: {e}")
        return self._email_client
    
    def get_secret(self, secret_name: str, default_value: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from Key Vault"""
        try:
            if self.key_vault_client:
                secret = self.key_vault_client.get_secret(secret_name)
                return secret.value
            else:
                logger.warning(f"Key Vault client not available, using default for {secret_name}")
                return default_value
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            return default_value
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in Key Vault"""
        try:
            if self.key_vault_client:
                self.key_vault_client.set_secret(secret_name, secret_value)
                logger.info(f"Secret {secret_name} stored successfully")
                return True
            else:
                logger.error("Key Vault client not available")
                return False
        except Exception as e:
            logger.error(f"Failed to store secret {secret_name}: {e}")
            return False

# Global Azure configuration instance
azure_config = AzureConfig()

def get_azure_config() -> AzureConfig:
    """Get the global Azure configuration instance"""
    return azure_config

# Helper functions for common operations
def get_database_url() -> str:
    """Get database URL from environment or Key Vault"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # Fallback to Key Vault
        db_url = azure_config.get_secret('database-url')
    
    if not db_url:
        raise ValueError("Database URL not configured in environment or Key Vault")
    
    return db_url

def get_jwt_secret() -> str:
    """Get JWT secret from Key Vault"""
    jwt_secret = azure_config.get_secret('jwt-secret-key')
    if not jwt_secret:
        # Generate and store a new secret if not exists
        import secrets
        jwt_secret = secrets.token_urlsafe(32)
        azure_config.set_secret('jwt-secret-key', jwt_secret)
        logger.info("Generated and stored new JWT secret")
    
    return jwt_secret

def get_google_oauth_config() -> tuple[str, str]:
    """Get Google OAuth configuration from Key Vault"""
    client_id = azure_config.get_secret('google-client-id')
    client_secret = azure_config.get_secret('google-client-secret')
    
    if not client_id or not client_secret:
        logger.warning("Google OAuth not configured in Key Vault")
        return "", ""
    
    return client_id, client_secret

def setup_monitoring():
    """Setup Azure Application Insights monitoring"""
    try:
        connection_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
        if connection_string:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            from opencensus.ext.azure.trace_exporter import AzureExporter
            from opencensus.trace.tracer import Tracer
            from opencensus.trace.samplers import ProbabilitySampler
            
            # Setup logging
            handler = AzureLogHandler(connection_string=connection_string)
            logging.getLogger().addHandler(handler)
            
            # Setup tracing
            tracer = Tracer(
                exporter=AzureExporter(connection_string=connection_string),
                sampler=ProbabilitySampler(1.0)
            )
            
            logger.info("Azure monitoring configured successfully")
            return tracer
    except Exception as e:
        logger.error(f"Failed to setup Azure monitoring: {e}")
    
    return None