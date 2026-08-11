import os
import stripe
import logging
from flask import Blueprint, request, jsonify, redirect
from api_rest.integracion.supabase_store import get_supabase_client
from api_rest.services.payment_service import payment_service

logger = logging.getLogger(__name__)
payment_bp = Blueprint("payment", __name__, url_prefix="/api/payment")

# Stripe Checkout Session (Fase D)
@payment_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json() or {}
    plan_code = data.get("plan_code", "pro")
    email = data.get("email")
    user_id = data.get("user_id")

    if not stripe.api_key:
        return jsonify({"error": "Stripe no configurado en backend", "url": "/planes?mock=1"}), 200

    # Map plan_code to Price ID (Mock or configure real ones in ENV)
    # In a real app, these come from ENV: os.getenv("STRIPE_PRICE_PRO")
    price_map = {
        "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_mock_123"),
        "faena": os.getenv("STRIPE_PRICE_FAENA", "price_faena_mock_456")
    }
    price_id = price_map.get(plan_code.lower())
    if not price_id:
        return jsonify({"error": "Plan inválido"}), 400

    # Ensure frontend URL
    frontend_url = os.getenv("METGO_CORS_ORIGINS", "https://metgo-quillota.pages.dev").split(",")[0]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/planes",
            customer_email=email,
            client_reference_id=user_id,
        )
        return jsonify({"url": session.url}), 200
    except Exception as e:
        logger.error(f"Stripe session error: {e}")
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    event = None
    if stripe.api_key and endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return "Invalid payload", 400
        except stripe.error.SignatureVerificationError as e:
            return "Invalid signature", 400
    else:
        # Modo mock / sin validar (Solo para dev local si no hay secrets)
        import json
        event = json.loads(payload.decode("utf-8"))

    # Manejar eventos de Stripe
    client = get_supabase_client()
    if not client:
        return jsonify({"error": "No db"}), 500

    try:
        event_type = event.get("type", "")
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session.get("client_reference_id")
            
            if user_id:
                # Update user plan in DB to 'pro'
                client.table("users").update({
                    "plan_code": "pro",
                    "sub_status": "active"
                }).eq("id", user_id).execute()
                logger.info(f"User {user_id} sub_status updated to active via checkout!")

        elif event_type == "customer.subscription.deleted":
            # Suscripción cancelada
            subscription = event["data"]["object"]
            # To actually map this back, we would need to store Stripe customer_id in Supabase.
            # Assuming we do, we could run:
            # client.table("users").update({"sub_status": "canceled"}).eq("stripe_customer_id", customer_id)
            pass
            
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return "Internal Error", 500

    return jsonify({"status": "success"}), 200
