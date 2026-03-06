import pytest
from fastapi import HTTPException

from app.core.security import require_viewer


def test_require_viewer_rejects_invalid_key() -> None:
    with pytest.raises(HTTPException):
        require_viewer(x_api_key="bad", api_key_qs=None)
