"""
security.py – Role-based API key authentication.

In APP_ENV=dev the viewer/editor roles are granted automatically when
no API key is supplied (to ease local development without a header).
In production, all requests MUST carry a valid X-API-Key header.
"""

from __future__ import annotations

from enum import Enum

from fastapi import Depends, Header, HTTPException, Query

from app.core.config import settings


class Role(str, Enum):
    ADMIN  = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


def _resolve_role(api_key: str | None) -> Role:
    # Dev shortcut: no key required when running locally
    if not api_key and settings.app_env in ("dev", "local", "development"):
        return Role.EDITOR  # grant editor in dev so all endpoints work

    if api_key == settings.api_key_admin:
        return Role.ADMIN
    if api_key == settings.api_key_editor:
        return Role.EDITOR
    if api_key == settings.api_key_viewer:
        return Role.VIEWER

    raise HTTPException(status_code=401, detail="Invalid or missing API key")


def require_viewer(
    x_api_key: str | None = Header(default=None),
    api_key_qs: str | None = Query(default=None, alias="x-api-key"),
) -> Role:
    return _resolve_role(x_api_key or api_key_qs)


def require_editor(role: Role = Depends(require_viewer)) -> Role:
    if role not in (Role.ADMIN, Role.EDITOR):
        raise HTTPException(status_code=403, detail="Editor role required")
    return role


def require_admin(role: Role = Depends(require_viewer)) -> Role:
    if role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    return role
