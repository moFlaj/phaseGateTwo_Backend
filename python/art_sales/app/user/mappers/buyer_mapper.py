from app.user.domain.order_model import Order
from app.user.dtos.requests.create_order_request import CreateOrderRequest

class Mapper:
    @staticmethod
    def from_request(req: CreateOrderRequest, buyer_id: str, artist_id: str, price: float):
        return Order(
            buyer_id=buyer_id,
            artist_id=artist_id,
            artwork_id=req.artwork_id,
            quantity=req.quantity,
            price=price,
            shipping=req.shipping_address or {},
        )
