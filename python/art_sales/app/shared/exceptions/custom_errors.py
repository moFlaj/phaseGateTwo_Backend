class AppError(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message or self.__class__.__name__)


# ─── Validation / Input ─────────────────────────────────────────────────────────
class ValidationError(AppError):
    """General input validation failure."""
    pass


class InvalidEmailFormatError(ValidationError):
    """Provided email is not in valid format."""
    pass


class InvalidArtworkPriceError(ValidationError):
    """Artwork price must be positive."""
    pass


class InvalidQuantityError(ValidationError):
    """Order quantity must be >= 1."""
    pass


class InvalidPriceRangeError(ValidationError):
    """Invalid price range for artwork search."""
    pass


class InvalidVerificationCodeError(AppError):
    pass


# ─── Resource Conflicts ─────────────────────────────────────────────────────────

# ─── Generic ────────────────────────────────────────────────────────────────────
class ResourceExistsError(AppError):
    """Generic resource already exists error (fallback)."""
    pass


class UserAlreadyExistsError(ResourceExistsError):
    """User with the given email already exists."""
    pass


class ArtworkAlreadyExistsError(ResourceExistsError):
    """Duplicate artwork title for this artist."""
    pass


class OrderAlreadyExistsError(ResourceExistsError):
    """Buyer already placed an order for this artwork."""
    pass


class NotFoundError(AppError):
    """Generic resource not found error (fallback)."""
    pass


# ─── Missing / Not Found ─────────────────────────────────────────────────────────
class ArtworkNotFoundError(NotFoundError):
    """Artwork could not be found."""
    pass


class OrderNotFoundError(NotFoundError):
    """Order not found in system."""
    pass


class VerificationNotFoundError(NotFoundError):
    """Verification record not found for user."""
    pass


# ─── Mail / Infrastructure ──────────────────────────────────────────────────────
class MailerSendError(AppError):
    """Email sending failed."""
    pass


class CartNotFoundError(NotFoundError):
    pass


class PaymentVerificationError(AppError):
    pass


class PaymentInitializationError(AppError):
    pass

class UnauthorizedOrderActionError(AppError):
    pass


class DuplicateOrderError(AppError):
    pass