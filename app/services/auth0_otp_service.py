"""
Auth0 Passwordless Email OTP Service

Handles Auth0 passwordless email verification:
1. start(email) - Triggers Auth0 to send OTP to user's email
2. verify(email, otp) - Verifies OTP with Auth0 and returns user info

Environment Variables Required:
- AUTH0_DOMAIN
- AUTH0_CLIENT_ID
- AUTH0_CLIENT_SECRET
- AUTH0_PASSWORDLESS_CONNECTION (usually "email")
- AUTH0_AUDIENCE (optional)
"""

import os
import httpx
from typing import Dict, Optional
from jose import jwt, JWTError
from jose.backends import RSAKey
from ..logging_config import get_logger

logger = get_logger(__name__)

# Cache for JWKS keys (in production, use proper caching with TTL)
_jwks_cache: Optional[Dict] = None


class Auth0OTPService:
    """Auth0 Passwordless Email OTP Service"""
    
    def __init__(self):
        self.domain = os.getenv("AUTH0_DOMAIN")
        self.client_id = os.getenv("AUTH0_CLIENT_ID")
        self.client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        self.connection = os.getenv("AUTH0_PASSWORDLESS_CONNECTION", "email")
        self.audience = os.getenv("AUTH0_AUDIENCE", "")
        self.issuer = f"https://{self.domain}/"
        
        if not all([self.domain, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing Auth0 configuration. Required: "
                "AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET"
            )
    
    async def _get_jwks(self) -> Dict:
        """Fetch JWKS (JSON Web Key Set) from Auth0"""
        global _jwks_cache
        
        if _jwks_cache is not None:
            return _jwks_cache
        
        jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(jwks_url)
                
                if response.status_code == 200:
                    _jwks_cache = response.json()
                    return _jwks_cache
                else:
                    logger.error(
                        "auth0_jwks_fetch_failed",
                        status_code=response.status_code
                    )
                    return {}
        except Exception as e:
            logger.error(
                "auth0_jwks_fetch_error",
                error=str(e)
            )
            return {}
    
    async def start(self, email: str) -> bool:
        """
        Trigger Auth0 to send OTP to user's email.
        
        Args:
            email: User's email address
            
        Returns:
            True if OTP was sent successfully, False otherwise
            
        Note:
            - OTP is NEVER logged or returned
            - Auth0 sends the email directly to the user
        """
        url = f"https://{self.domain}/passwordless/start"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "connection": self.connection,
            "email": email,
            "send": "code",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    logger.info(
                        "auth0_otp_sent",
                        email=email,
                        status="success"
                    )
                    return True
                else:
                    logger.warning(
                        "auth0_otp_failed",
                        email=email,
                        status_code=response.status_code,
                        error=response.text
                    )
                    return False
                    
        except Exception as e:
            logger.error(
                "auth0_otp_exception",
                email=email,
                error=str(e)
            )
            return False
    
    async def verify(self, email: str, otp: str) -> Optional[Dict[str, any]]:
        """
        Verify OTP with Auth0 and return user info.
        
        Args:
            email: User's email address
            otp: 6-digit OTP code from email
            
        Returns:
            Dict with user info if successful:
            {
                "email": "user@example.com",
                "email_verified": True,
                "sub": "auth0|xxx",
                "name": "User Name" (optional)
            }
            
            None if verification failed
            
        Note:
            - OTP is NEVER logged
            - Only returns sanitized user info
        """
        url = f"https://{self.domain}/oauth/token"
        
        payload = {
            "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": email,
            "otp": otp,
            "realm": self.connection,
            "scope": "openid email profile",
        }
        
        if self.audience:
            payload["audience"] = self.audience
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code != 200:
                    logger.warning(
                        "auth0_verify_failed",
                        email=email,
                        status_code=response.status_code
                    )
                    return None
                
                token_data = response.json()
                id_token = token_data.get("id_token")
                
                if not id_token:
                    logger.error(
                        "auth0_no_id_token",
                        email=email
                    )
                    return None
                
                # Verify JWT signature and claims with Auth0's public key
                try:
                    # Fetch JWKS for signature verification
                    jwks = await self._get_jwks()
                    
                    # Decode header to get key ID
                    unverified_header = jwt.get_unverified_header(id_token)
                    kid = unverified_header.get("kid")
                    
                    if not kid:
                        logger.error("auth0_jwt_no_kid", email=email)
                        return None
                    
                    # Find the matching key in JWKS
                    rsa_key = None
                    for key in jwks.get("keys", []):
                        if key.get("kid") == kid:
                            rsa_key = {
                                "kty": key.get("kty"),
                                "kid": key.get("kid"),
                                "use": key.get("use"),
                                "n": key.get("n"),
                                "e": key.get("e")
                            }
                            break
                    
                    if not rsa_key:
                        logger.error(
                            "auth0_jwt_key_not_found",
                            email=email,
                            kid=kid
                        )
                        return None
                    
                    # Verify and decode JWT with full validation
                    claims = jwt.decode(
                        id_token,
                        rsa_key,
                        algorithms=["RS256"],
                        audience=self.client_id,  # aud should match client_id for id_token
                        issuer=self.issuer
                    )
                    
                    # Validate email_verified claim
                    email_verified = claims.get("email_verified", False)
                    if not email_verified:
                        logger.warning(
                            "auth0_email_not_verified",
                            email=email
                        )
                        return None
                    
                    # Validate email matches
                    token_email = claims.get("email")
                    if token_email != email:
                        logger.error(
                            "auth0_email_mismatch",
                            expected=email,
                            got=token_email
                        )
                        return None
                    
                    user_info = {
                        "email": claims.get("email"),
                        "email_verified": email_verified,
                        "sub": claims.get("sub"),
                        "name": claims.get("name"),
                    }
                    
                    logger.info(
                        "auth0_verify_success",
                        email=email,
                        email_verified=user_info["email_verified"]
                    )
                    
                    return user_info
                    
                except JWTError as e:
                    logger.error(
                        "auth0_jwt_decode_error",
                        email=email,
                        error=str(e)
                    )
                    return None
                    
        except Exception as e:
            logger.error(
                "auth0_verify_exception",
                email=email,
                error=str(e)
            )
            return None


# Singleton instance
_auth0_service: Optional[Auth0OTPService] = None


def get_auth0_otp_service() -> Auth0OTPService:
    """Get or create Auth0 OTP service instance"""
    global _auth0_service
    if _auth0_service is None:
        _auth0_service = Auth0OTPService()
    return _auth0_service
