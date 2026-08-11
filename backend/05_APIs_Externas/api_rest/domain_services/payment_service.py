import logging
import os

logger = logging.getLogger(__name__)

try:
    import stripe
except ImportError:  # pragma: no cover - entorno sin stripe (tests locales)
    stripe = None

# Initialize stripe
stripe_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
if stripe is not None and stripe_key:
    stripe.api_key = stripe_key


class PaymentService:
    def create_customer(self, email: str, name: str) -> str:
        """Crear cliente en Stripe o devolver mock si no hay key"""
        if stripe is None or not getattr(stripe, "api_key", None):
            logger.warning("Stripe is not configured. Using mock.")
            return f"mock_cus_{email}"

        try:
            customer = stripe.Customer.create(email=email, name=name)
            return customer.id
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise

    def create_subscription(self, customer_id: str, price_id: str) -> dict:
        """Crear suscripción en Stripe"""
        if stripe is None or not getattr(stripe, "api_key", None):
            logger.warning("Stripe is not configured. Using mock.")
            return {"id": "mock_sub_123", "status": "active", "client_secret": None}

        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
            )

            client_secret = None
            if subscription.latest_invoice and subscription.latest_invoice.payment_intent:
                client_secret = subscription.latest_invoice.payment_intent.client_secret

            return {
                "id": subscription.id,
                "status": subscription.status,
                "client_secret": client_secret,
            }
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            raise


payment_service = PaymentService()
