from typing import Any

import requests

from app.domain.models.models import SocialProvider


class SocialAuthService:
    """
    Servicio encargado de validar tokens emitidos por proveedores externos.
    """
    @staticmethod
    async def verify_google_token(token: str) -> dict[str, Any] | None:
        """Valida un ID Token con los servidores de Google."""
        try:
            # Endpoint de Google para validación de tokens
            response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "social_id": data["sub"],
                    "email": data.get("email"),
                    "full_name": data.get("name"),
                    "image_url": data.get("picture")
                }
        except Exception:
            return None
        return None

    @staticmethod
    async def verify_facebook_token(token: str) -> dict[str, Any] | None:
        """Valida un Access Token con el Graph API de Facebook."""
        try:
            url = f"https://graph.facebook.com/me?fields=id,name,email,picture&access_token={token}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "social_id": data["id"],
                    "email": data.get("email"),
                    "full_name": data.get("name"),
                    "image_url": data.get("picture", {}).get("data", {}).get("url")
                }
        except Exception:
            return None
        return None

    @staticmethod
    async def verify_apple_token(token: str) -> dict[str, Any] | None:
        """
        Valida un token de Apple. 
        Requiere validación de firma con llaves públicas de Apple.
        """
        # Implementación simplificada (placeholder)
        return None 

    async def get_social_user(self, provider: SocialProvider, token: str) -> dict[str, Any] | None:
        """
        Método unificado para obtener datos de usuario según el proveedor.
        """
        if provider == SocialProvider.GOOGLE:
            return await self.verify_google_token(token)
        elif provider == SocialProvider.FACEBOOK:
            return await self.verify_facebook_token(token)
        elif provider == SocialProvider.APPLE:
            return await self.verify_apple_token(token)
        return None