"""Tests for the current modem endpoint collection behavior."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.ziggo_modem.api import (
    ZiggoModemApi,
    ZiggoModemApiError,
    ZiggoModemAuthError,
)


def make_api() -> ZiggoModemApi:
    """Create an API client without making HTTP requests."""
    return ZiggoModemApi("192.168.178.1", "", "secret", MagicMock())


def set_endpoint_results(api: ZiggoModemApi) -> None:
    """Provide representative results for every polled endpoint."""
    api.async_get_state = AsyncMock(return_value={"cablemodem": {"upTime": 42}})
    api.async_get_downstream = AsyncMock(return_value={"downstream": {}})
    api.async_get_primary_downstream = AsyncMock(return_value={})
    api.async_get_upstream = AsyncMock(return_value={"upstream": {}})
    api.async_get_serviceflows = AsyncMock(return_value={"serviceFlows": []})
    api.async_get_softwareupdate = AsyncMock(return_value={})


@pytest.mark.parametrize(
    ("username", "expected_payload"),
    [
        ("", {"password": "secret"}),
        ("admin", {"username": "admin", "password": "secret"}),
    ],
)
async def test_login_payload_supports_password_only_modems(
    username, expected_payload
):
    """The username field is omitted unless the user configured one."""
    response = MagicMock(status=200)
    response.text = AsyncMock(return_value="")
    response.json = AsyncMock(return_value={"created": {"token": "test-token"}})
    session = MagicMock(closed=False)
    session.post.return_value.__aenter__ = AsyncMock(return_value=response)
    session.post.return_value.__aexit__ = AsyncMock(return_value=None)
    api = ZiggoModemApi("192.168.178.1", username, "secret", session)

    await api.async_login()

    assert session.post.call_args.kwargs["json"] == expected_payload


async def test_all_endpoints_succeed():
    """A successful poll preserves the endpoint names and status values."""
    api = make_api()
    set_endpoint_results(api)

    data = await api.async_get_data()

    assert data["state"]["cablemodem"]["upTime"] == 42
    assert set(data) == {
        "state",
        "downstream",
        "primary_downstream",
        "upstream",
        "serviceflows",
        "softwareupdate",
    }
    assert set(api.last_endpoint_status.values()) == {"ok"}


async def test_one_endpoint_failure_keeps_other_results():
    """One failed endpoint does not discard successful endpoint results."""
    api = make_api()
    set_endpoint_results(api)
    api.async_get_downstream = AsyncMock(side_effect=ZiggoModemApiError("offline"))

    data = await api.async_get_data()

    assert data["downstream"] == {}
    assert data["state"]["cablemodem"]["upTime"] == 42
    assert api.last_endpoint_status["downstream"] == "failed"
    assert api.last_endpoint_status["state"] == "ok"


async def test_authentication_failure_is_not_treated_as_partial_data():
    """An auth error still triggers reauthentication after gathering endpoints."""
    api = make_api()
    set_endpoint_results(api)
    api.async_get_state = AsyncMock(side_effect=ZiggoModemAuthError("invalid"))

    with pytest.raises(ZiggoModemAuthError):
        await api.async_get_data()

    assert api.last_endpoint_status["state"] == "failed"
