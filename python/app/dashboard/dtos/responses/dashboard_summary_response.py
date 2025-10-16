from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class DashboardSummaryResponse:
    """DTO returned when a user loads their dashboard."""
    success: bool
    message: str
    role: str
    summary: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to serializable dict for Flask jsonify."""
        return asdict(self)
