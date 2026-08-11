import stripe
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    """Servicio de pagos y suscripciones con Stripe"""
    
    def create_customer(self, email: str, name: str) -> str:
        """Crear cliente en Stripe"""
        if not settings.STRIPE_SECRET_KEY:
            logger.warning("Stripe is not configured")
            return f"mock_cus_{email}"
            
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
            )
            return customer.id
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise

    def create_subscription(self, customer_id: str, price_id: str) -> dict:
        """Crear suscripción en Stripe"""
        if not settings.STRIPE_SECRET_KEY:
            logger.warning("Stripe is not configured")
            return {"id": "mock_sub_123", "status": "active"}
            
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
            )
            return {
                "id": subscription.id,
                "status": subscription.status,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice and subscription.latest_invoice.payment_intent else None
            }
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            raise

payment_service = PaymentService()
