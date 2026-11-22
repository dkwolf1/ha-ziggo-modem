"""Tests for the DOCSIS version exposed by the modem status sensor."""

from unittest.mock import MagicMock

import pytest

from custom_components.ziggo_modem.sensor import SENSORS, ZiggoModemSensor


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"state": {"cablemodem": {"model": "F3896", "docsisVersion": "3.1"}}}, "3.1"),
        ({"state": {"system": {"docsisVersion": " DOCSIS 4.0 "}}}, "4.0"),
        (
            {
                "state": {"cablemodem": {"docsisVersion": "unknown"}},
                "softwareupdate": {"softwareUpdate": {"docsisVersion": "3.1"}},
            },
            "3.1",
        ),
        ({"state": {"cablemodem": {"docsisVersion": "unknown"}}}, None),
        ({"state": None, "softwareupdate": None}, None),
        ({}, None),
    ],
)
def test_status_exposes_the_reported_docsis_version(data, expected):
    coordinator = MagicMock(data=data, language="en")
    description = next(item for item in SENSORS if item.key == "status")
    sensor = ZiggoModemSensor(coordinator, "test-entry", "modem.local", description)

    assert sensor.extra_state_attributes == (
        {"docsis_version": expected} if expected is not None else None
    )
