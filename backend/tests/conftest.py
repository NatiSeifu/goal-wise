"""Global test safety settings."""

import os

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["SECURE_COOKIES"] = "false"
os.environ["COOKIE_SAMESITE"] = "lax"
os.environ["ALLOWED_FRONTEND_ORIGIN"] = "http://localhost:5173"
