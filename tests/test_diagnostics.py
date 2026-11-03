"""Tests for redaction in downloaded integration diagnostics."""

from types import SimpleNamespace

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ziggo_modem.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)
from custom_components.ziggo_modem.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_redacts_known_sensitive_fields(hass):
    """Entry credentials and nested modem identifiers stay out of downloads."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.178.1",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "very-secret-password",
        },
    )
    entry.add_to_hass(hass)
    entry.runtime_data = SimpleNamespace(
        coordinator=SimpleNamespace(
            last_successful_update=None,
            last_exception=None,
            last_update_success=True,
            consecutive_failures=0,
            max_failures=3,
            update_interval_seconds=60,
            endpoint_status={"state": "ok"},
            is_paused=False,
            verbose_diagnostics=False,
            language="en",
            signal_thresholds={},
            problem_history={},
            data={
                "state": {
                    "cablemodem": {
                        "serialNumber": "private-serial",
                        "macAddress": "aa:bb:cc:dd:ee:ff",
                        "accessToken": "private-token",
                    }
                }
            },
        )
    )

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    serialized = str(diagnostics)

    for secret in (
        "192.168.178.1",
        "admin",
        "very-secret-password",
        "private-serial",
        "aa:bb:cc:dd:ee:ff",
        "private-token",
    ):
        assert secret not in serialized
    assert diagnostics["runtime"]["endpoint_status"] == {"state": "ok"}
