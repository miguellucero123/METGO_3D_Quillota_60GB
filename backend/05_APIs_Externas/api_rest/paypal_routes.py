import os
import logging
from flask import Blueprint, request, jsonify

from api_rest.integracion.supabase_store import get_supabase_client
from api_rest.domain_services.paypal_service import paypal_service

logger = logging.getLogger(__name__)
paypal_bp = Blueprint("paypal", __name__, url_prefix="/api/paypal")

@paypal_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json() or {}
    plan_code = data.get("plan_code", "pro")
    email = data.get("email")
    user_id = data.get("user_id")

    # Ensure frontend URL
    frontend_url = os.getenv("METGO_CORS_ORIGINS", "https://metgo-quillota.pages.dev").split(",")[0]
    if frontend_url == "*":
        frontend_url = "http://localhost:5173"
        
    return_url = f"{frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}&payment_status=success"
    cancel_url = f"{frontend_url}/planes"

    try:
        order = paypal_service.create_order(
            plan_code=plan_code, 
            email=email, 
            user_id=user_id,
            return_url=return_url,
            cancel_url=cancel_url
        )
        return jsonify({"url": order.get("url"), "order_id": order.get("id")}), 200
    except Exception as e:
        logger.error(f"PayPal session error: {e}")
        return jsonify({"error": str(e)}), 500

@paypal_bp.route("/capture-order", methods=["POST"])
def capture_order():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    user_id = data.get("user_id")
    plan_code = data.get("plan_code", "pro")
    
    if not order_id:
        return jsonify({"error": "order_id es requerido"}), 400
        
    try:
        result = paypal_service.capture_order(order_id)
        if result.get("status") == "COMPLETED":
            # Update user plan in DB
            client = get_supabase_client()
            if client and user_id:
                client.table("users").update({
                    "plan_code": plan_code,
                    "sub_status": "active"
                }).eq("id", user_id).execute()
                logger.info(f"User {user_id} sub_status updated to active via PayPal!")
                
            return jsonify({"status": "success", "message": "Pago completado exitosamente"}), 200
        else:
            return jsonify({"status": "failed", "message": "El pago no pudo ser completado"}), 400
    except Exception as e:
        logger.error(f"PayPal capture error: {e}")
        return jsonify({"error": str(e)}), 500
