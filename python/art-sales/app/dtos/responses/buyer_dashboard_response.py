# app/dtos/responses/buyer_dashboard_response.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class BuyerDashboardResponse:
    success: bool
    message: str
    orders: List[Dict]   # list of orders, each dict with item/price
