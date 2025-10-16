# app/buyer/services/cart_service.py
from app.user.persistence.cart_repository import CartRepository
from app.user.domain.cart_model import Cart, CartItem
from app.user.persistence.artwork_repository import ArtworkRepository
from app.user.dtos.requests.add_to_cart_request import AddToCartRequest
from app.user.dtos.requests.checkout_request import CheckoutRequest
from app.user.dtos.responses.cart_response import CartResponse
from app.shared.exceptions.custom_errors import (
    ArtworkNotFoundError,
    CartNotFoundError,
)
import os

class CartService:
    def __init__(self, cart_repo: CartRepository, artwork_repo: ArtworkRepository):
        self.cart_repo = cart_repo
        self.artwork_repo = artwork_repo

    def add_to_cart(self, buyer_id: str, req: AddToCartRequest) -> CartResponse:
        req.validate()
        artwork = self.artwork_repo.find_by_id(req.artwork_id)
        if not artwork:
            raise ArtworkNotFoundError("Artwork not found.")

        item = CartItem(
            artwork_id=req.artwork_id,
            title=artwork.get("title"),
            price=artwork.get("price"),
            quantity=req.quantity,
        )
        cart = Cart(buyer_id=buyer_id, items=[item])
        cart_id = self.cart_repo.create(cart.to_dict())
        return CartResponse(success=True, message="Item added to cart", cart_id=cart_id, total_amount=cart.total_amount())

    def get_cart(self, buyer_id: str) -> dict:
        """Get active cart for buyer."""
        cart_doc = self.cart_repo.find_by_buyer(buyer_id)
        if not cart_doc:
            return {"success": True, "cart": {"items": [], "total": 0.0}}
        
        return {
            "success": True, 
            "cart": {
                "cart_id": str(cart_doc["_id"]),
                "items": cart_doc["items"],
                "total": sum(i["price"] * i["quantity"] for i in cart_doc["items"])
            }
        }

    def checkout(self, req: CheckoutRequest) -> dict:
        req.validate()
        cart_doc = self.cart_repo.find_by_id(req.cart_id)
        if not cart_doc:
            raise CartNotFoundError("Cart not found.")

        total_amount = sum(i["price"] * i["quantity"] for i in cart_doc["items"])
        # For Paystack integration, we don't need to create a payment intent here
        # The checkout controller will handle creating the Paystack session
        return {
            "success": True,
            "message": "Cart ready for checkout",
            "total_amount": total_amount
        }