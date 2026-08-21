import logging
import os

logger = logging.getLogger(__name__)

# Intentar importar la librería oficial de PayPal si se quiere, 
# pero generalmente para la API REST directa usamos requests.
import requests
from requests.auth import HTTPBasicAuth

PAYPAL_CLIENT_ID = (os.getenv("PAYPAL_CLIENT_ID") or "").strip()
PAYPAL_SECRET = (os.getenv("PAYPAL_SECRET") or "").strip()
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox").strip().lower()

if PAYPAL_MODE == "live":
    PAYPAL_API_BASE = "https://api-m.paypal.com"
else:
    PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"


class PayPalService:
    def _get_access_token(self) -> str:
        """Obtiene un access token de PayPal."""
        if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
            logger.warning("PayPal no está configurado. Usando token mock.")
            return "mock_access_token"

        url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                auth=HTTPBasicAuth(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
                timeout=10
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            logger.error(f"Error obteniendo token de PayPal: {e}")
            raise

    def create_order(self, plan_code: str, email: str, user_id: str, return_url: str, cancel_url: str) -> dict:
        """Crea una orden de cobro en PayPal."""
        if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
            logger.warning("PayPal no está configurado. Usando mock order.")
            return {"id": "mock_order_123", "status": "CREATED", "url": "/dashboard?session_id=mock_order_123"}
            
        # Determinar precio según plan (simplificado para MVP)
        price = "99.00" if plan_code == "pro" else "299.00"
        
        token = self._get_access_token()
        url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(user_id) if user_id else "guest",
                    "description": f"Plan {plan_code.upper()} METGO3D",
                    "amount": {
                        "currency_code": "USD",
                        "value": price
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "METGO3D",
                        "locale": "es-CL",
                        "landing_page": "LOGIN",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": cancel_url
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Buscar link de aprobación
            approve_url = next((link["href"] for link in data.get("links", []) if link["rel"] == "payer-action"), cancel_url)
            
            return {
                "id": data["id"],
                "status": data["status"],
                "url": approve_url
            }
        except Exception as e:
            logger.error(f"Error creando orden PayPal: {e}")
            raise

    def capture_order(self, order_id: str) -> dict:
        """Captura los fondos de una orden aprobada por el usuario."""
        if order_id.startswith("mock_order"):
            return {"status": "COMPLETED"}
            
        token = self._get_access_token()
        url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error capturando orden PayPal: {e}")
            raise


paypal_service = PayPalService()
