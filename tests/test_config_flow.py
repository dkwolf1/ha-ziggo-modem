"""Tests for setup, reauthentication, reconfiguration, and options flows."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import voluptuous as vol
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ziggo_modem.api import ZiggoModemApiError, ZiggoModemAuthError
from custom_components.ziggo_modem.config_flow import _create_api
from custom_components.ziggo_modem.const import (
    CONF_DOWNSTREAM_POWER_MAX,
    CONF_DOWNSTREAM_POWER_MIN,
    CONF_DOWNSTREAM_SNR_MIN,
    CONF_HOST,
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_UPSTREAM_POWER_MAX,
    CONF_USERNAME,
    CONF_VERBOSE_DIAGNOSTICS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


@pytest.fixture
def mock_api():
    """Replace modem login so flows never contact a real device."""
    api = MagicMock()
    api.async_login = AsyncMock()
    api.async_close = AsyncMock()
    with patch(
        "custom_components.ziggo_modem.config_flow._create_api",
        return_value=api,
    ):
        yield api


@pytest.fixture
def mock_setup_entry():
    """Avoid setting up entities after a successful user flow."""
    with patch(
        "custom_components.ziggo_modem.async_setup_entry",
        new_callable=AsyncMock,
        return_value=True,
    ) as setup:
        yield setup


def user_input(host="192.168.178.1", username=""):
    """Return a valid setup form submission."""
    return {
        CONF_HOST: host,
        CONF_USERNAME: username,
        CONF_PASSWORD: "secret",
        CONF_LANGUAGE: "en",
    }


def modem_entry(host="192.168.100.1", *, unique_id=None, options=None):
    """Return an existing modem entry for flow tests."""
    return MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id=host if unique_id is None else unique_id,
        data={
            CONF_HOST: host,
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "old-secret",
        },
        options=options if options is not None else {CONF_SCAN_INTERVAL: 90},
    )


def test_create_api_uses_home_assistant_session(hass):
    """The flow passes the shared Home Assistant session to its API client."""
    session = MagicMock()
    with patch(
        "custom_components.ziggo_modem.config_flow.async_get_clientsession",
        return_value=session,
    ) as get_session:
        api = _create_api(hass, "192.168.178.1", "", "secret")

    get_session.assert_called_once_with(hass, verify_ssl=False)
    assert api.host == "192.168.178.1"
    assert api._session is session


async def test_user_flow_creates_unique_entry(hass, mock_api, mock_setup_entry):
    """Setup stores connection data separately from configurable options."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input("192.168.178.1", "admin")
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "192.168.178.1"
    assert result["data"] == {
        CONF_HOST: "192.168.178.1",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }
    assert result["options"][CONF_LANGUAGE] == "en"
    assert result["options"][CONF_SCAN_INTERVAL] == DEFAULT_SCAN_INTERVAL
    mock_api.async_login.assert_awaited_once()
    mock_api.async_close.assert_awaited_once()


@pytest.mark.parametrize(
    ("failure", "error"),
    [
        (ZiggoModemAuthError("invalid"), "invalid_auth"),
        (ZiggoModemApiError("offline"), "cannot_connect"),
        (RuntimeError("unexpected"), "unknown"),
    ],
)
async def test_user_flow_recovers_from_login_errors(
    hass, mock_api, mock_setup_entry, failure, error
):
    """A user can retry setup after each reported login error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    mock_api.async_login.side_effect = failure

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input()
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    mock_api.async_login.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input()
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "192.168.178.1"
    assert mock_api.async_close.await_count == 2


async def test_user_flow_rejects_duplicate_modem(hass, mock_api):
    """An existing modem cannot be configured at the same address twice."""
    modem_entry("192.168.178.1").add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input()
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_rejects_duplicate_unique_id(hass, mock_api):
    """A legacy entry with another address still protects its unique ID."""
    entry = modem_entry(unique_id="192.168.178.1")
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input()
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_updates_existing_entry(hass):
    """A new address keeps the entry, options and entity IDs intact."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="192.168.100.1",
        data={CONF_HOST: "192.168.100.1", CONF_PASSWORD: "secret"},
        options={"scan_interval": 90},
    )
    entry.add_to_hass(hass)
    api = MagicMock()
    api.async_login = AsyncMock()
    api.async_close = AsyncMock()

    with (
        patch(
            "custom_components.ziggo_modem.config_flow._create_api",
            return_value=api,
        ),
        patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
        )
        assert result["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: "192.168.178.1"},
        )

    assert result["type"] is FlowResultType.ABORT
    assert entry.data[CONF_HOST] == "192.168.178.1"
    assert entry.unique_id == "192.168.178.1"
    assert entry.options == {"scan_interval": 90}


@pytest.mark.parametrize(
    ("failure", "error"),
    [
        (ZiggoModemAuthError("invalid"), "invalid_auth"),
        (ZiggoModemApiError("offline"), "cannot_connect"),
        (RuntimeError("unexpected"), "unknown"),
    ],
)
async def test_reconfigure_recovers_from_login_errors(
    hass, mock_api, failure, error
):
    """An address change can be retried without replacing the entry."""
    entry = modem_entry()
    entry.add_to_hass(hass)
    mock_api.async_login.side_effect = failure

    with patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "192.168.178.1"}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": error}
        assert entry.data[CONF_HOST] == "192.168.100.1"

        mock_api.async_login.side_effect = None
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "192.168.178.1"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_HOST] == "192.168.178.1"
    assert entry.unique_id == "192.168.178.1"


async def test_reconfigure_recovers_from_duplicate_address(hass, mock_api):
    """A conflicting address can be replaced with a free one in the form."""
    entry = modem_entry()
    entry.add_to_hass(hass)
    modem_entry("192.168.178.1").add_to_hass(hass)

    with patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "192.168.178.1"}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "already_configured"}
        mock_api.async_login.assert_not_awaited()

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "192.168.178.2"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_HOST] == "192.168.178.2"


@pytest.mark.parametrize(
    ("failure", "error"),
    [
        (ZiggoModemAuthError("invalid"), "invalid_auth"),
        (ZiggoModemApiError("offline"), "cannot_connect"),
        (RuntimeError("unexpected"), "unknown"),
    ],
)
async def test_reauth_recovers_from_login_errors(
    hass, mock_api, failure, error
):
    """New credentials can be submitted after each reauthentication error."""
    entry = modem_entry()
    entry.add_to_hass(hass)
    mock_api.async_login.side_effect = failure

    with patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock):
        result = await entry.start_reauth_flow(hass)
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "reauth_confirm"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USERNAME: "", CONF_PASSWORD: "new-secret"}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": error}
        assert entry.data[CONF_PASSWORD] == "old-secret"

        mock_api.async_login.side_effect = None
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USERNAME: "", CONF_PASSWORD: "new-secret"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_USERNAME] == ""
    assert entry.data[CONF_PASSWORD] == "new-secret"
    assert entry.unique_id == "192.168.100.1"
    assert entry.options == {CONF_SCAN_INTERVAL: 90}


async def test_options_flow_uses_current_values_and_saves_changes(hass):
    """Options remain independent of modem connection credentials."""
    entry = modem_entry(options={CONF_SCAN_INTERVAL: 90, CONF_LANGUAGE: "nl"})
    entry.add_to_hass(hass)

    with patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock):
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "init"
        defaults = result["data_schema"]({})
        assert defaults[CONF_SCAN_INTERVAL] == 90
        assert defaults[CONF_LANGUAGE] == "nl"
        with pytest.raises(vol.Invalid):
            result["data_schema"]({CONF_SCAN_INTERVAL: 4})

        new_options = {
            CONF_SCAN_INTERVAL: 120,
            CONF_DOWNSTREAM_POWER_MIN: -12.0,
            CONF_DOWNSTREAM_POWER_MAX: 12.0,
            CONF_DOWNSTREAM_SNR_MIN: 35.0,
            CONF_UPSTREAM_POWER_MAX: 53.0,
            CONF_VERBOSE_DIAGNOSTICS: True,
            CONF_LANGUAGE: "en",
        }
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], new_options
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == new_options
    assert entry.data[CONF_PASSWORD] == "old-secret"
