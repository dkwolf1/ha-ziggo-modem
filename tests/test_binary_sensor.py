"""Tests for existing binary-sensor parsing and cable thresholds."""

import pytest

from custom_components.ziggo_modem.binary_sensor import (
    analyze_cable_issue,
    normalize_access_allowed,
)
from custom_components.ziggo_modem.const import (
    CONF_DOWNSTREAM_POWER_MIN,
    CONF_DOWNSTREAM_SNR_MIN,
    CONF_UPSTREAM_POWER_MAX,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        (" YES ", True),
        ("denied", False),
        ("unknown", None),
        (None, None),
    ],
)
def test_access_allowed_normalization(raw, expected):
    """Known modem values retain their current interpretation."""
    assert normalize_access_allowed(raw) is expected


def test_cable_issue_uses_configured_thresholds():
    """Custom thresholds change classification without changing readings."""
    data = {
        "state": {"cablemodem": {"upTime": 3600}},
        "downstream": {
            "downstream": {
                "channels": [
                    {
                        "channelType": "sc_qam",
                        "lockStatus": True,
                        "snr": 30,
                        "power": -13,
                    }
                ]
            }
        },
        "upstream": {
            "upstream": {
                "channels": [
                    {
                        "channelType": "atdma",
                        "power": 54,
                        "t3Timeout": 0,
                        "t4Timeout": 0,
                    }
                ]
            }
        },
    }

    default = analyze_cable_issue(data)
    configured = analyze_cable_issue(
        data,
        {
            CONF_DOWNSTREAM_POWER_MIN: -15,
            CONF_DOWNSTREAM_SNR_MIN: 28,
            CONF_UPSTREAM_POWER_MAX: 55,
        },
    )

    assert set(default["reason_codes"]) == {
        "downstream_snr_low",
        "downstream_power_out_of_range",
        "upstream_power_high",
    }
    assert configured["reason_codes"] == []
