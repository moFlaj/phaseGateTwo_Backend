# app/buyer/services/order_service.py
from typing import List, Dict
from app.user.persistence.order_repository import OrderRepository
from app.user.persistence.artwork_repository import ArtworkRepository
from app.user.dtos.requests.create_order_request import CreateOrderRequest
from app.user.dtos.responses.order_response import OrderResponse
from app.user.mappers.buyer_mapper import Mapper
from app.shared.exceptions.custom_errors import (
    ArtworkNotFoundError,
    InvalidQuantityError,
    OrderAlreadyExistsError,
    OrderNotFoundError,
    ValidationError, UnauthorizedOrderActionError,
)


class OrderService:
    def __init__(self, order_repo: OrderRepository, artwork_repo: ArtworkRepository = None):
        self.order_repo = order_repo
        self.artwork_repo = artwork_repo or ArtworkRepository()

    def create_order(self, buyer_id: str, req: CreateOrderRequest, cart_id: str = None) -> OrderResponse:
        req.validate()
        if req.quantity <= 0:
            raise InvalidQuantityError("Order quantity must be >= 1.")

        artwork = self.artwork_repo.find_by_id(req.artwork_id)
        if not artwork:
            raise ArtworkNotFoundError("Artwork not found.")

        if self.order_repo.find_duplicate(buyer_id, req.artwork_id):
            raise OrderAlreadyExistsError("You already ordered this artwork.")

        price = float(artwork.get("price", 0)) * req.quantity
        order_model = Mapper.from_request(req, buyer_id, artwork.get("artist_id"), price)
        order_dict = order_model.to_dict()
        order_dict["cart_id"] = cart_id

        order_id = self.order_repo.create(order_dict)
        return OrderResponse(success=True, message="Order created", order_id=order_id)

    def list_orders_by_buyer(self, buyer_id: str, limit: int = 50, skip: int = 0) -> list:
        """List orders for a specific buyer."""
        docs = self.order_repo.find_by_buyer(buyer_id, limit=limit, skip=skip)
        for doc in docs:
            doc["order_id"] = str(doc.pop("_id"))
        return docs

    def list_orders_by_artist(self, artist_id: str, limit: int = 50, skip: int = 0) -> list:
        """List orders for a specific artist."""
        docs = self.order_repo.find_by_artist(artist_id, limit=limit, skip=skip)
        for doc in docs:
            doc["order_id"] = str(doc.pop("_id"))
        return docs

    def ship_order(self, order_id: str, artist_id: str) -> dict:
        """Artist marks order as shipped."""
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError("Order not found.")
        if order.get("artist_id") != artist_id:
            raise UnauthorizedOrderActionError("You cannot update another artist's order.")
        if order.get("status") != "processing":
            raise ValidationError("Can only ship orders that are being processed.")

        updated = self.order_repo.update_status(order_id, "shipped")
        if not updated:
            raise ValidationError("Order update failed.")
        return {"success": True, "message": "Order marked as shipped. Buyer will be notified."}

    def confirm_receipt(self, order_id: str, buyer_id: str) -> dict:
        """Buyer confirms receipt of artwork."""
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError("Order not found.")
        if order.get("buyer_id") != buyer_id:
            raise UnauthorizedOrderActionError("You can only confirm your own orders.")
        if order.get("status") == "completed":
            raise ValidationError("Order already confirmed as received.")
        if order.get("status") != "shipped":
            raise ValidationError("Order must be shipped before you can confirm receipt.")

        updated = self.order_repo.update_status(order_id, "completed")
        if not updated:
            raise ValidationError("Order update failed.")
        return {"success": True, "message": "Order confirmed as received. Payment released to artist."}

    def complete_order(self, order_id: str, artist_id: str) -> dict:
        """Legacy method - now marks as shipped instead of completed."""
        return self.ship_order(order_id, artist_id)

    def mark_paid_by_cart(self, cart_id: str):
        """Called from Stripe webhook handler."""
        count = self.order_repo.mark_paid_by_cart(cart_id)
        return {"success": True, "updated": count}
