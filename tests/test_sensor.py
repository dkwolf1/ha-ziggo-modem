"""Tests for recent DOCSIS counter rates."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from custom_components.ziggo_modem.sensor import SENSORS, ZiggoModemSensor


@pytest.mark.parametrize(
    ("key", "endpoint", "channel_type", "counter"),
    [
        ("ofdm_errors_delta_rate", "downstream", "ofdm", "uncorrectedErrors"),
        ("scqam_errors_delta_rate", "downstream", "sc_qam", "uncorrectedErrors"),
        ("t3_timeouts_delta_rate", "upstream", "atdma", "t3Timeout"),
    ],
)
def test_delta_rate_uses_only_fresh_endpoint_samples(key, endpoint, channel_type, counter):
    coordinator = MagicMock(language="en")
    description = next(item for item in SENSORS if item.key == key)
    sensor = ZiggoModemSensor(coordinator, "test-entry", "modem.local", description)
    start = datetime(2026, 11, 21, tzinfo=UTC)

    def sample(total, minute=None):
        coordinator.data = {
            endpoint: {endpoint: {"channels": [
                {"channelType": channel_type, counter: total}
            ]}},
            "state": {},
        }
        coordinator.fresh_endpoint_sample_time.return_value = (
            None if minute is None else start + timedelta(minutes=minute)
        )
        return sensor.native_value

    assert sample(10) is None  # No fresh baseline yet.
    assert sample(10, 0) == 0
    assert sample(11, 1) == 60
    assert sample(11) == 60  # Other endpoints updated; this counter is cached.
    assert sample(11) == 60
    assert sample(13, 5) == 30  # Two new counts spread over four minutes.
    assert sample(13, 5) == 30  # Re-reading the same poll is not a new sample.
    assert sample(0, 6) == 0  # Counter reset.
    assert sample(1, 7) == 60
    coordinator.fresh_endpoint_sample_time.assert_called_with(endpoint)
