# app/services/buyer_service.py
from app.dtos.requests.buyer_update_profile_request import BuyerUpdateProfileRequest
from app.dtos.requests.cart_item_request import CartItemRequest
from app.dtos.responses.order_history_response import OrderHistoryResponse
from app.persistence.buyer_repository import BuyerRepository

class BuyerService:
    def __init__(self, buyer_repository: BuyerRepository):
        self.buyer_repository = buyer_repository

    # --- Profile ---
    def update_profile(self, buyer_id: str, request_dto: BuyerUpdateProfileRequest):
        request_dto.validate()
        update_data = {k: v for k, v in vars(request_dto).items() if v is not None}
        success = self.buyer_repository.update_profile(buyer_id, update_data)
        return {"success": success, "message": "Profile updated" if success else "Nothing updated"}

    # --- Cart ---
    def add_to_cart(self, buyer_id: str, request_dto: CartItemRequest):
        request_dto.validate()
        self.buyer_repository.add_to_cart(buyer_id, request_dto.artwork_id, request_dto.quantity)
        return {"success": True, "message": "Added to cart"}

    def get_cart(self, buyer_id: str):
        items = self.buyer_repository.get_cart(buyer_id)
        return {"success": True, "items": items}

    # --- Orders ---
    def get_order_history(self, buyer_id: str) -> OrderHistoryResponse:
        orders = self.buyer_repository.get_orders(buyer_id)
        return OrderHistoryResponse(success=True, message="Orders fetched", orders=orders)
