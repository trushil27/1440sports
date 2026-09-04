"""Sign-in (build brief §8): passkey primary, magic link for enrolment/recovery only.

- Allowlist: exactly the addresses in APP_USERS. Anyone else gets a silent no-op (the
  magic-link endpoint returns 204 either way; nothing is sent).
- Magic link: signed, single-purpose, ``magic_link_minutes`` TTL, sent from the 1440
  mailbox through the pipeline's mailer (no new service). Verifying it sets the session
  and marks the user enrolled; the next step in the app is registering a passkey.
- Passkey (WebAuthn): registration requires a session; login is by discoverable
  credential or by email → allow-list of that user's credentials. Challenges live in a
  short-lived signed cookie.
- Session: signed cookie, ``session_days`` (90), refreshed silently on every request
  that is older than a day.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from intel import send as send_mod
from intel.config import get_settings
from intel.models_auth import AppUser, Passkey
from intel_api.settings import ApiSettings, User

SESSION_COOKIE = "intel_session"
CHALLENGE_COOKIE = "intel_wa_challenge"

router = APIRouter(prefix="/auth", tags=["auth"])


def _serializer(settings: ApiSettings, salt: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt=salt)


# --- session cookies ---------------------------------------------------------------------


@dataclass
class SessionUser:
    email: str
    role: str
    display_name: str
    issued_at: float


def issue_session(response: Response, settings: ApiSettings, user: User) -> None:
    now = dt.datetime.now(dt.UTC).timestamp()
    token = _serializer(settings, "session").dumps(
        {"e": user.email, "r": user.role, "n": user.display_name, "t": now}
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def read_session(request: Request, settings: ApiSettings) -> SessionUser | None:
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    try:
        data = _serializer(settings, "session").loads(raw, max_age=settings.session_days * 86400)
    except (BadSignature, SignatureExpired):
        return None
    user = settings.user(data.get("e"))
    if user is None:  # removed from the allowlist → session dies
        return None
    return SessionUser(user.email, user.role, user.display_name, float(data.get("t", 0)))


def clear_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


# --- dependencies (imported by the app) ---------------------------------------------------


def get_api_settings(request: Request) -> ApiSettings:
    return request.app.state.api_settings


def get_db(request: Request) -> Session:
    return request.state.db


def current_user(
    request: Request, response: Response, settings: ApiSettings = Depends(get_api_settings)
) -> SessionUser:
    user = read_session(request, settings)
    if user is None:
        raise HTTPException(status_code=401, detail="sign in required")
    # silent refresh once a day
    if dt.datetime.now(dt.UTC).timestamp() - user.issued_at > 86400:
        issue_session(response, settings, User(user.email, user.role, user.display_name))
    return user


def require_operator(user: SessionUser = Depends(current_user)) -> SessionUser:
    if user.role != "operator":
        raise HTTPException(status_code=403, detail="operator only")
    return user


# --- magic link --------------------------------------------------------------------------


class MagicLinkRequest(BaseModel):
    email: str


def magic_link_token(settings: ApiSettings, email: str) -> str:
    return _serializer(settings, "magic-link").dumps({"e": email.lower()})


def verify_magic_link_token(settings: ApiSettings, token: str) -> str | None:
    try:
        data = _serializer(settings, "magic-link").loads(
            token, max_age=settings.magic_link_minutes * 60
        )
    except (BadSignature, SignatureExpired):
        return None
    return data.get("e")


@router.post("/magic-link", status_code=204)
def request_magic_link(
    body: MagicLinkRequest,
    request: Request,
    settings: ApiSettings = Depends(get_api_settings),
) -> Response:
    """Always 204. Only an allow-listed address actually gets a link (silent no-op otherwise)."""
    user = settings.user(body.email)
    if user is not None:
        token = magic_link_token(settings, user.email)
        link = f"{settings.api_base_url}/auth/magic-link/verify?token={token}"
        mailer = getattr(request.app.state, "mailer", None) or send_mod.mailer_for(get_settings())
        mailer.send(
            send_mod.Outgoing(
                to=[user.email],
                subject="Your 1440 Intelligence sign-in link",
                body_text=(
                    "Sign in to 1440 Intelligence "
                    f"(link valid {settings.magic_link_minutes} minutes):\n\n"
                    f"{link}\n\nAfter signing in, add a passkey (Face ID / Touch ID) so you never "
                    "need a link again.\n\nIf you did not request this, ignore it."
                ),
            )
        )
    return Response(status_code=204)


@router.get("/magic-link/verify")
def verify_magic_link(
    token: str,
    response: Response,
    settings: ApiSettings = Depends(get_api_settings),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    email = verify_magic_link_token(settings, token)
    user = settings.user(email)
    if user is None:
        raise HTTPException(status_code=400, detail="link invalid or expired")
    now = dt.datetime.now(dt.UTC)
    row = db.scalar(select(AppUser).where(AppUser.email == user.email))
    if row is None:
        row = AppUser(
            email=user.email, role=user.role, display_name=user.display_name, enrolled_at=now
        )
        db.add(row)
    row.last_login_at = now
    row.enrolled_at = row.enrolled_at or now
    db.flush()
    issue_session(response, settings, user)
    has_passkey = db.scalar(select(Passkey).where(Passkey.user_email == user.email)) is not None
    return {
        "email": user.email,
        "role": user.role,
        "has_passkey": has_passkey,
        "next": "/enrol" if not has_passkey else "/",
    }


@router.post("/logout", status_code=204)
def logout() -> Response:
    response = Response(status_code=204)
    clear_session(response)
    return response


@router.get("/me")
def me(user: SessionUser = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    n = len(db.scalars(select(Passkey).where(Passkey.user_email == user.email)).all())
    return {
        "email": user.email,
        "role": user.role,
        "display_name": user.display_name,
        "passkeys": n,
    }


# --- passkeys (WebAuthn) ----------------------------------------------------------------------


def _set_challenge(
    response: Response, settings: ApiSettings, challenge: bytes, email: str | None
) -> None:
    token = _serializer(settings, "wa-challenge").dumps({"c": challenge.hex(), "e": email})
    response.set_cookie(
        CHALLENGE_COOKIE,
        token,
        max_age=300,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/auth",
    )


def _pop_challenge(request: Request, settings: ApiSettings) -> tuple[bytes, str | None]:
    raw = request.cookies.get(CHALLENGE_COOKIE)
    if not raw:
        raise HTTPException(status_code=400, detail="no pending challenge")
    try:
        data = _serializer(settings, "wa-challenge").loads(raw, max_age=300)
    except (BadSignature, SignatureExpired) as exc:
        raise HTTPException(status_code=400, detail="challenge expired") from exc
    return bytes.fromhex(data["c"]), data.get("e")


@router.post("/passkey/register/options")
def passkey_register_options(
    response: Response,
    user: SessionUser = Depends(current_user),
    settings: ApiSettings = Depends(get_api_settings),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    from webauthn import generate_registration_options, options_to_json
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        PublicKeyCredentialDescriptor,
        ResidentKeyRequirement,
        UserVerificationRequirement,
    )

    existing = db.scalars(select(Passkey).where(Passkey.user_email == user.email)).all()
    opts = generate_registration_options(
        rp_id=settings.rp_id,
        rp_name=settings.rp_name,
        user_id=user.email.encode(),
        user_name=user.email,
        user_display_name=user.display_name or user.email,
        exclude_credentials=[PublicKeyCredentialDescriptor(id=p.credential_id) for p in existing],
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    _set_challenge(response, settings, opts.challenge, user.email)
    return json.loads(options_to_json(opts))


class PasskeyVerifyBody(BaseModel):
    credential: dict[str, Any]
    device_name: str | None = None


@router.post("/passkey/register/verify")
def passkey_register_verify(
    body: PasskeyVerifyBody,
    request: Request,
    response: Response,
    user: SessionUser = Depends(current_user),
    settings: ApiSettings = Depends(get_api_settings),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    from webauthn import verify_registration_response

    challenge, email = _pop_challenge(request, settings)
    if email != user.email:
        raise HTTPException(status_code=400, detail="challenge does not belong to this session")
    try:
        verified = verify_registration_response(
            credential=body.credential,
            expected_challenge=challenge,
            expected_rp_id=settings.rp_id,
            expected_origin=settings.origin,
            require_user_verification=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"passkey registration failed: {exc}") from exc
    transports = body.credential.get("response", {}).get("transports")
    db.add(
        Passkey(
            user_email=user.email,
            credential_id=verified.credential_id,
            public_key=verified.credential_public_key,
            sign_count=verified.sign_count,
            transports=transports,
            device_name=body.device_name,
        )
    )
    db.flush()
    response.delete_cookie(CHALLENGE_COOKIE, path="/auth")
    return {"ok": True}


class PasskeyLoginOptionsBody(BaseModel):
    email: str | None = None


@router.post("/passkey/login/options")
def passkey_login_options(
    body: PasskeyLoginOptionsBody,
    response: Response,
    settings: ApiSettings = Depends(get_api_settings),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    from webauthn import generate_authentication_options, options_to_json
    from webauthn.helpers.structs import PublicKeyCredentialDescriptor, UserVerificationRequirement

    allow: list[PublicKeyCredentialDescriptor] = []
    user = settings.user(body.email) if body.email else None
    if user is not None:
        rows = db.scalars(select(Passkey).where(Passkey.user_email == user.email)).all()
        allow = [PublicKeyCredentialDescriptor(id=p.credential_id) for p in rows]
    opts = generate_authentication_options(
        rp_id=settings.rp_id,
        allow_credentials=allow,  # empty → discoverable credential (Face ID picks the account)
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    _set_challenge(response, settings, opts.challenge, user.email if user else None)
    return json.loads(options_to_json(opts))


@router.post("/passkey/login/verify")
def passkey_login_verify(
    body: PasskeyVerifyBody,
    request: Request,
    response: Response,
    settings: ApiSettings = Depends(get_api_settings),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    from webauthn import verify_authentication_response
    from webauthn.helpers import base64url_to_bytes

    challenge, _email = _pop_challenge(request, settings)
    raw_id = body.credential.get("rawId") or body.credential.get("id")
    if not raw_id:
        raise HTTPException(status_code=400, detail="credential id missing")
    cred_id = base64url_to_bytes(raw_id)
    row = db.scalar(select(Passkey).where(Passkey.credential_id == cred_id))
    user = settings.user(row.user_email) if row else None
    if row is None or user is None:
        raise HTTPException(status_code=401, detail="unknown passkey")
    try:
        verified = verify_authentication_response(
            credential=body.credential,
            expected_challenge=challenge,
            expected_rp_id=settings.rp_id,
            expected_origin=settings.origin,
            credential_public_key=row.public_key,
            credential_current_sign_count=row.sign_count,
            require_user_verification=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"passkey verification failed: {exc}") from exc
    row.sign_count = verified.new_sign_count
    row.last_used_at = dt.datetime.now(dt.UTC)
    app_user = db.scalar(select(AppUser).where(AppUser.email == user.email))
    if app_user is not None:
        app_user.last_login_at = row.last_used_at
    db.flush()
    response.delete_cookie(CHALLENGE_COOKIE, path="/auth")
    issue_session(response, settings, user)
    return {"email": user.email, "role": user.role}
