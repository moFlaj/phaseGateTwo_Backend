from dataclasses import dataclass

@dataclass
class UserSignupRequest:
    name: str
    email: str
    password: str
    role: str

    def validate(self):

        if not self.name:
            raise ValueError("Name is required")
        if not self.email or "@" not in self.email:
            raise ValueError("Valid email is required")
        if not self.password or len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if self.role not in ["artist", "buyer"]:
            raise ValueError("Role must be 'artist' or 'buyer'")
