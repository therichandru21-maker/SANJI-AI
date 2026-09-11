# backend/app/config.py

import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# GOOGLE OAUTH
# ============================================================

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


# ============================================================
# JWT
# ============================================================

JWT_SECRET = os.getenv("JWT_SECRET")


# ============================================================
# VALIDATION
# ============================================================

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not configured."
    )


if not GOOGLE_CLIENT_ID:
    raise ValueError(
        "GOOGLE_CLIENT_ID is not configured."
    )


if not GOOGLE_CLIENT_SECRET:
    raise ValueError(
        "GOOGLE_CLIENT_SECRET is not configured."
    )


if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET is not configured."
    )