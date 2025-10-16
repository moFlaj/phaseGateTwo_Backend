# app/buyer/services/buyer_service.py
from app.user.persistence.artwork_repository import ArtworkRepository
from app.shared.exceptions.custom_errors import ValidationError
from app.user.persistence.order_repository import OrderRepository
from app.user.services.s3_service import S3Service


class BuyerService:
    def __init__(self, order_repo: OrderRepository, artwork_repo: ArtworkRepository = None):
        self.order_repo = order_repo
        self.artwork_repo = artwork_repo or ArtworkRepository()

    def buyer_summary(self, buyer_id: str) -> dict:
        if not buyer_id:
            raise ValidationError("Buyer email required.")
        orders = self.order_repo.find_by_buyer(buyer_id)
        total_orders = len(orders)
        completed = sum(1 for o in orders if o.get("status") == "completed")
        pending = sum(1 for o in orders if o.get("status") == "processing")
        total_spent = sum(o.get("price", 0) for o in orders if o.get("status") == "completed")
        
        # Add wallet information if wallet service is available
        wallet_info = {}
        try:
            from app.wallet.controllers.wallet_controller import wallet_service
            if wallet_service:
                wallet = wallet_service.get_wallet(buyer_id)
                if wallet:
                    wallet_info["wallet_balance"] = wallet.balance
                    wallet_info["wallet_currency"] = wallet.currency
                else:
                    # Wallet doesn't exist yet
                    wallet_info["wallet_balance"] = None
                    wallet_info["wallet_currency"] = "NGN"  # Default currency
        except Exception as e:
            # If there's any issue with wallet service, continue without it
            print(f"DEBUG: Error accessing wallet service: {e}")
        
        return {
            "total_orders": total_orders,
            "completed_orders": completed,
            "pending_orders": pending,
            "total_spent": round(total_spent, 2),
            **wallet_info
        }

    def search_artworks(self,
                        query: str | None = None,
                        min_price: float = 0.0,
                        max_price: float = 1_000_000.0,
                        limit: int = 50,
                        skip: int = 0) -> list:
        """
        Validate and delegate search to ArtworkRepository.
        """
        # pagination validation
        try:
            limit = int(limit)
            skip = int(skip)
        except Exception:
            raise ValidationError("Invalid pagination parameters.")

        if limit <= 0 or skip < 0:
            raise ValidationError("Invalid pagination parameters.")

        # delegate to repository (it performs price validation)
        results = self.artwork_repo.search_artworks(query=query, min_price=min_price, max_price=max_price, limit=limit,
                                                 skip=skip)
        
        # Add image URLs for artworks with S3 keys
        s3_service = S3Service()
        for artwork in results:
            s3_key = artwork.get("s3_key")
            if s3_key:
                try:
                    artwork["image_url"] = s3_service.generate_get_url(s3_key, expires_in=3600)
                except Exception:
                    # If we can't generate URL, just skip it
                    pass
                    
        return results