# app/buyer/services/paystack_checkout_service.py
from app.user.persistence.cart_repository import CartRepository
from app.user.persistence.order_repository import OrderRepository
from app.shared.exceptions.custom_errors import ValidationError
from app.wallet.services.paystack_service import PaystackService
from typing import Dict, Any, Optional


class PaystackCheckoutService:
    """Service for handling Paystack checkout operations."""
    
    def __init__(self, cart_repo: CartRepository, order_repo: OrderRepository = None):
        self.cart_repo = cart_repo
        self.order_repo = order_repo or OrderRepository()
        self.paystack_service = PaystackService()

    def create_checkout_session(self, buyer_id: str, cart_id: str) -> Dict[str, Any]:
        """
        Create a Paystack checkout session for the cart items.
        Returns a Paystack payment URL that the frontend can redirect to.
        """
        # Validate cart exists and belongs to buyer
        cart = self.cart_repo.find_by_id_and_buyer(cart_id, buyer_id)
        if not cart:
            raise ValidationError("Cart not found or does not belong to user")
            
        # Calculate total amount
        total_amount = 0
        items = cart.get("items", [])
        if not items:
            raise ValidationError("Cart is empty")
            
        for item in items:
            price = item.get("price", 0)
            quantity = item.get("quantity", 1)
            total_amount += price * quantity
            
        if total_amount <= 0:
            raise ValidationError("Cart total must be greater than zero")
            
        # Get buyer email (you might need to fetch this from user service)
        # If buyer_id is already an email, use it directly, otherwise create a placeholder
        if "@" in buyer_id:
            buyer_email = buyer_id
        else:
            buyer_email = f"buyer_{buyer_id}@example.com"  # Placeholder - replace with real email lookup
        
        # Generate reference ID for this transaction
        reference = f"order_{cart_id}_{int(__import__('time').time())}"
        
        # Create Paystack transaction
        response = self.paystack_service.initialize_transaction(
            email=buyer_email,
            amount=int(total_amount * 100),  # Convert to kobo
            reference=reference,
            metadata={
                "cart_id": cart_id,
                "buyer_id": buyer_id,
                "items": items
            }
        )
        
        if not response.get("status"):
            raise ValidationError("Failed to initialize Paystack transaction")
            
        data = response.get("data", {})
        
        # Create pending orders for each item in cart
        order_ids = []
        for item in items:
            order_data = {
                "buyer_id": buyer_id,
                "artwork_id": item.get("artwork_id"),
                "quantity": item.get("quantity", 1),
                "price": item.get("price", 0),
                "status": "pending",
                "reference": reference
            }
            order_id = self.order_repo.create(order_data)
            order_ids.append(str(order_id))
        
        return {
            "authorization_url": data.get("authorization_url"),
            "access_code": data.get("access_code"),
            "reference": data.get("reference"),
            "amount": total_amount,
            "order_ids": order_ids
        }

    def verify_payment(self, reference: str, email_service: Optional[Any] = None) -> Dict[str, Any]:
        """
        Verify a Paystack payment and update order statuses.
        """
        # Verify the transaction with Paystack
        response = self.paystack_service.verify_transaction(reference)
        
        if not response.get("status"):
            raise ValidationError("Failed to verify Paystack transaction")
            
        data = response.get("data", {})
        if data.get("status") != "success":
            raise ValidationError("Payment was not successful")
            
        # Get the cart ID from the metadata to delete the cart
        metadata = data.get("metadata", {})
        cart_id = metadata.get("cart_id")
        
        # Update orders to completed status
        updated_count = self.order_repo.mark_paid_by_reference(reference)
        
        # Delete the cart if we have a cart ID
        if cart_id:
            try:
                self.cart_repo.delete(cart_id)
            except Exception as e:
                # Log the error but don't fail the payment verification
                print(f"Warning: Failed to delete cart {cart_id}: {e}")
        
        # Send emails if email service is provided
        if email_service and cart_id:
            try:
                # Get the orders that were just updated
                orders = self.order_repo.find_by_reference(reference)
                if orders:
                    # Send confirmation email to buyer
                    buyer_email = data.get("customer", {}).get("email", "buyer@example.com")
                    email_service.send_email(
                        recipient_email=buyer_email,
                        subject="Order Confirmed",
                        body=f"Your payment has been confirmed. Reference: {reference}"
                    )
                    
                    # Send notification to artists
                    for order in orders:
                        artist_email = "artist@example.com"  # This should be looked up from the artwork
                        email_service.send_email(
                            recipient_email=artist_email,
                            subject="New sale",
                            body=f"A new order has been placed. Reference: {reference}"
                        )
            except Exception as e:
                # Log the error but don't fail the payment verification
                print(f"Warning: Failed to send emails: {e}")
                
        return {
            "success": True,
            "message": f"Payment verified and {updated_count} orders updated",
            "reference": reference
        }