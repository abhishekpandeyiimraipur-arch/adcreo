"""
POST /auth/google
Verifies a Google ID token, upserts the user, and returns a signed JWT.
"""

import os
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
JWT_SECRET       = os.environ.get("JWT_SECRET", "dev-secret-change-in-prod")
JWT_ALGO         = "HS256"
TOKEN_TTL_HOURS  = 24


class GoogleAuthRequest(BaseModel):
    credential: str


@router.post("/google")
async def google_auth(body: GoogleAuthRequest, request: Request) -> dict:
    """
    1. Verify Google ID token via google-auth library
    2. Upsert user row (beta_invited=TRUE on insert, credits_remaining=0)
    3. Return {"token": <HS256 JWT>}
    """
    # ── Step 1: Verify Google ID token ───────────────────────────────────
    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        logger.warning("google_token_invalid: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    google_id = idinfo["sub"]
    email     = idinfo["email"]
    name      = idinfo.get("name", "")

    # ── Step 2: Upsert into users ─────────────────────────────────────────
    db = request.app.state.db
    try:
        row = await db.fetchrow(
            """
            INSERT INTO users
                (google_id, email, name, plan_tier, credits_remaining,
                 session_version, beta_invited)
            VALUES
                ($1, $2, $3, 'pro', 5, 1, TRUE)
            ON CONFLICT (google_id) DO UPDATE
                SET name       = EXCLUDED.name,
                    updated_at = NOW()
            RETURNING user_id, plan_tier, session_version
            """,
            google_id, email, name,
        )
    except Exception as exc:
        logger.error("google_auth_db_error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Database error during sign-in")

    # ── Step 2b: Seed Redis wallet (DB0) for new users ───────────────────
    try:
        redis_mgr = request.app.state.redis_mgr
        await redis_mgr.db0.hsetnx(
            f"wallet:{str(row['user_id'])}", "balance", 5
        )
    except Exception as exc:
        logger.warning("redis_wallet_seed_failed user_id=%s: %s", row["user_id"], exc)
        # Non-fatal — JWT still issued; wallet can be seeded manually if needed

    # ── Step 3: Mint HS256 JWT ────────────────────────────────────────────
    claims = {
        "sub":             str(row["user_id"]),
        "user_id":         str(row["user_id"]),
        "plan_tier":       row["plan_tier"],
        "session_version": row["session_version"],
        "exp":             datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS),
    }
    token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALGO)

    logger.info("google_auth_ok user_id=%s email=%s", row["user_id"], email)
    return {"token": token}
