"""Tests for the /notifications endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.tests.utils.user import create_random_user


# ---------------------------------------------------------------------------
# WebSocket — authentication
# ---------------------------------------------------------------------------

def test_websocket_rejects_missing_token(client: TestClient) -> None:
    """WebSocket connection without a token should be rejected."""
    with pytest.raises(Exception):
        with client.websocket_connect(
            f"{settings.API_V1_STR}/notifications/ws"
        ) as ws:
            ws.receive_text()


def test_websocket_rejects_invalid_token(client: TestClient) -> None:
    """WebSocket connection with a bad JWT should be rejected."""
    with pytest.raises(Exception):
        with client.websocket_connect(
            f"{settings.API_V1_STR}/notifications/ws?token=not-a-jwt"
        ) as ws:
            ws.receive_text()


def test_websocket_accepts_valid_token(
    db,  # type: ignore[no-untyped-def]
    normal_user_token_headers: dict[str, str],
) -> None:
    """WebSocket token authentication should work with valid JWT."""
    from backend.api.routes.notifications import _get_user_from_token
    from backend.tests.utils.user import create_random_user
    from backend.core.security import create_access_token
    from datetime import timedelta
    from backend.core.config import settings

    # Create a test user
    user = create_random_user(db)

    # Create a valid JWT token for this user
    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(hours=1),
    )

    # Authenticate using the token
    authenticated_user = _get_user_from_token(token, db)
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.email == user.email


# ---------------------------------------------------------------------------
# POST /notifications/send  (superuser only)
# ---------------------------------------------------------------------------


def test_send_notification_superuser(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db,  # type: ignore[no-untyped-def]
) -> None:
    """Superuser can send a notification to any user."""
    target = create_random_user(db)

    with patch(
        "backend.api.routes.notifications.publish_notification",
        new_callable=AsyncMock,
    ) as mock_pub:
        response = client.post(
            f"{settings.API_V1_STR}/notifications/send",
            headers=superuser_token_headers,
            json={
                "user_id": str(target.id),
                "type": "info",
                "title": "Hello",
                "message": "World",
            },
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Notification sent"
    mock_pub.assert_called_once()
    channel_arg, payload_arg = mock_pub.call_args.args
    assert str(target.id) in channel_arg
    assert "Hello" in payload_arg


def test_send_notification_requires_superuser(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db,  # type: ignore[no-untyped-def]
) -> None:
    """Non-superusers should receive 403 when calling /send."""
    target = create_random_user(db)

    response = client.post(
        f"{settings.API_V1_STR}/notifications/send",
        headers=normal_user_token_headers,
        json={
            "user_id": str(target.id),
            "type": "info",
            "title": "Hi",
            "message": "There",
        },
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /notifications/send/me
# ---------------------------------------------------------------------------


def test_send_notification_to_self(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Any authenticated user can send a notification to themselves."""
    with patch(
        "backend.api.routes.notifications.publish_notification",
        new_callable=AsyncMock,
    ) as mock_pub:
        response = client.post(
            f"{settings.API_V1_STR}/notifications/send/me",
            headers=normal_user_token_headers,
            json={
                "type": "success",
                "title": "Test",
                "message": "It works",
            },
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Notification sent"
    mock_pub.assert_called_once()
    _channel, payload = mock_pub.call_args.args
    assert "Test" in payload
    assert "success" in payload


def test_send_notification_to_self_requires_auth(client: TestClient) -> None:
    """Unauthenticated requests to /send/me should receive 401/403."""
    response = client.post(
        f"{settings.API_V1_STR}/notifications/send/me",
        json={"type": "info", "title": "X", "message": "Y"},
    )
    assert response.status_code in {401, 403}


def test_send_notification_validates_payload(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Requests with invalid notification type should fail validation."""
    response = client.post(
        f"{settings.API_V1_STR}/notifications/send/me",
        headers=normal_user_token_headers,
        json={
            "type": "invalid-type",
            "title": "Oops",
            "message": "Bad type",
        },
    )
    assert response.status_code == 422
