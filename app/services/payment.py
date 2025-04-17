import uuid
from app.config import settings
from app.models.booking import PaymentStatus

# Mock payment gateway integration
async def process_payment(amount: float, card_number: str, expiry_date: str, cvv: str):
    # In a real-world scenario, this would call an external payment gateway API
    # For this mock implementation, we'll simulate a successful payment for most cases
    
    # Mock validation
    if len(card_number) < 13 or len(card_number) > 19:
        return {"status": PaymentStatus.FAILED, "payment_id": None, "message": "Invalid card number"}
    
    if len(cvv) != 3:
        return {"status": PaymentStatus.FAILED, "payment_id": None, "message": "Invalid CVV"}
    
    # Generate payment ID (normally would come from payment gateway)
    payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
    
    # Mock success/failure (95% success rate for demo)
    import random
    if random.random() < 0.95:
        return {
            "status": PaymentStatus.COMPLETED,
            "payment_id": payment_id,
            "message": "Payment processed successfully"
        }
    else:
        return {
            "status": PaymentStatus.FAILED,
            "payment_id": None,
            "message": "Payment processing failed. Please try again."
        }

async def refund_payment(payment_id: str):
    # Mock refund process
    # In a real-world scenario, this would call the payment gateway's refund API
    return {
        "status": PaymentStatus.REFUNDED,
        "payment_id": payment_id,
        "message": "Refund processed successfully"
    }