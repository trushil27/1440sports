"""API settings (environment), layered on the pipeline's ``intel.config.Settings``."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class User:
    email: str
    role: str  # "operator" | "md"
    display_name: str = ""


def _parse_users(raw: str | None) -> list[User]:
    """APP_USERS="trushil@x.com:operator:Trushil,ricky@x.com:md:Ricky" (exactly the allowlist)."""
    out: list[User] = []
    for part in (raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split(":")
        email = bits[0].strip().lower()
        role = (bits[1].strip().lower() if len(bits) > 1 else "md") or "md"
        name = bits[2].strip() if len(bits) > 2 else ""
        if role not in ("operator", "md"):
            raise ValueError(f"APP_USERS role must be operator or md, got {role!r}")
        out.append(User(email, role, name))
    return out


@dataclass(frozen=True)
class ApiSettings:
    secret_key: str
    users: list[User] = field(default_factory=list)
    rp_id: str = "localhost"  # WebAuthn relying-party id = the app's host
    rp_name: str = "1440 Intelligence"
    origin: str = "http://localhost:3000"  # the web app origin (exact, incl. scheme)
    api_base_url: str = "http://localhost:8000"
    session_days: int = 90
    magic_link_minutes: int = 15
    cookie_secure: bool = False
    contact_provider: str = "none"  # apollo once approved (§11.7)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> ApiSettings:
        e = dict(os.environ if env is None else env)
        secret = e.get("APP_SECRET_KEY")
        if not secret:
            # A missing secret must never silently produce a guessable one in production.
            if e.get("EXECUTION_MODE", "shadow") == "production":
                raise RuntimeError("APP_SECRET_KEY is required in production")
            secret = "dev-only-insecure-secret"
        return cls(
            secret_key=secret,
            users=_parse_users(e.get("APP_USERS")),
            rp_id=e.get("APP_RP_ID", "localhost"),
            rp_name=e.get("APP_RP_NAME", "1440 Intelligence"),
            origin=e.get("APP_ORIGIN", "http://localhost:3000"),
            api_base_url=e.get("API_BASE_URL", "http://localhost:8000"),
            session_days=int(e.get("APP_SESSION_DAYS", "90")),
            magic_link_minutes=int(e.get("APP_MAGIC_LINK_MINUTES", "15")),
            cookie_secure=e.get("APP_COOKIE_SECURE", "false").lower() == "true",
            contact_provider=e.get("CONTACT_PROVIDER", "none"),
        )

    def user(self, email: str | None) -> User | None:
        if not email:
            return None
        email = email.strip().lower()
        for u in self.users:
            if u.email == email:
                return u
        return None
