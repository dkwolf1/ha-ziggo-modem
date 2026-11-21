"""Bridge the legacy and official Home Assistant test packages."""

from importlib.util import find_spec

HAS_OFFICIAL_TEST_PLUGIN = find_spec("pytest_homeassistant") is not None

if HAS_OFFICIAL_TEST_PLUGIN:
    from pytest_homeassistant.common import MockConfigEntry
else:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

__all__ = ["MockConfigEntry"]
