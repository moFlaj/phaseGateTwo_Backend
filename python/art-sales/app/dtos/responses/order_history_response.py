# app/dtos/responses/order_history_response.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class OrderHistoryResponse:
    success: bool
    message: str
    orders: List[Dict]  # each dict: artwork_id, title, price, quantity, total_price, date
