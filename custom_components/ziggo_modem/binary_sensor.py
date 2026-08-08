from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DOWNSTREAM_POWER_MAX,
    CONF_DOWNSTREAM_POWER_MIN,
    CONF_DOWNSTREAM_SNR_MIN,
    CONF_HOST,
    CONF_UPSTREAM_POWER_MAX,
    DEFAULT_DOWNSTREAM_POWER_MAX,
    DEFAULT_DOWNSTREAM_POWER_MIN,
    DEFAULT_DOWNSTREAM_SNR_MIN,
    DEFAULT_UPSTREAM_POWER_MAX,
    DOMAIN,
    ENDPOINT_DOWNSTREAM,
    ENDPOINT_STATE,
    ENDPOINT_UPSTREAM,
)
from .entity import ZiggoModemBaseEntity


def get_ds_channels(data):
    return data.get("downstream", {}).get("downstream", {}).get("channels", [])


def get_us_channels(data):
    return data.get("upstream", {}).get("upstream", {}).get("channels", [])


def scqam_ds(ch):
    return [c for c in ch if c.get("channelType") == "sc_qam"]


def ofdm_ds(ch):
    return [c for c in ch if c.get("channelType") == "ofdm"]


def scqam_us(ch):
    return [c for c in ch if c.get("channelType") == "atdma"]


def avg(lst, key):
    vals = [c[key] for c in lst if key in c]
    return round(sum(vals) / len(vals), 1) if vals else None


def minv(lst, key):
    vals = [c[key] for c in lst if key in c]
    return min(vals) if vals else None


def sumv(lst, key):
    return sum(c.get(key, 0) for c in lst)


def locked(lst):
    return sum(1 for c in lst if c.get("lockStatus"))


def normalize_access_allowed(value: Any) -> bool | None:
    """Return accessAllowed as a boolean when the modem value is recognized."""
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value == 1:
            return True
        if value == 0:
            return False

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "allowed", "yes", "1"}:
            return True
        if normalized in {"false", "denied", "no", "0"}:
            return False

    return None


def internet_access_allowed(data) -> bool:
    value = data.get("state", {}).get("cablemodem", {}).get("accessAllowed")
    return normalize_access_allowed(value) is True


def internet_outage(data) -> bool:
    value = data.get("state", {}).get("cablemodem", {}).get("accessAllowed")
    return normalize_access_allowed(value) is False


def analyze_cable_issue(
    data,
    thresholds: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Return cable issue causes and the measurements used to detect them."""
    thresholds = thresholds or {}
    downstream_power_min = float(
        thresholds.get(
            CONF_DOWNSTREAM_POWER_MIN,
            DEFAULT_DOWNSTREAM_POWER_MIN,
        )
    )
    downstream_power_max = float(
        thresholds.get(
            CONF_DOWNSTREAM_POWER_MAX,
            DEFAULT_DOWNSTREAM_POWER_MAX,
        )
    )
    downstream_snr_min = float(
        thresholds.get(
            CONF_DOWNSTREAM_SNR_MIN,
            DEFAULT_DOWNSTREAM_SNR_MIN,
        )
    )
    upstream_power_max = float(
        thresholds.get(
            CONF_UPSTREAM_POWER_MAX,
            DEFAULT_UPSTREAM_POWER_MAX,
        )
    )

    ds_all = get_ds_channels(data)
    us_all = get_us_channels(data)

    ds_scqam = scqam_ds(ds_all)
    ds_ofdm = ofdm_ds(ds_all)
    us_scqam = scqam_us(us_all)

    ds_snr = minv(ds_scqam, "snr")
    ds_power = avg(ds_scqam, "power")
    us_power = avg(us_scqam, "power")
    ds_locked = locked(ds_all)
    ds_total = len(ds_all)

    # Include uptime so counters are evaluated as rates per hour.
    uptime = data.get("state", {}).get("cablemodem", {}).get("upTime", 0)
    hours = max(uptime / 3600, 1 / 60)

    ofdm_uncorrected_total = sumv(ds_ofdm, "uncorrectedErrors")
    t3_timeouts_total = sumv(us_all, "t3Timeout")
    t4_timeouts_total = sumv(us_all, "t4Timeout") if us_all else 0

    ofdm_rate = ofdm_uncorrected_total / hours
    t3_rate = t3_timeouts_total / hours
    reason_codes: list[str] = []

    if ds_total and ds_locked < ds_total:
        reason_codes.append("downstream_channels_unlocked")

    if ds_snr is not None and ds_snr < downstream_snr_min - 1:
        reason_codes.append("downstream_snr_low")

    if ds_power is not None and (
        ds_power < downstream_power_min - 2
        or ds_power > downstream_power_max + 2
    ):
        reason_codes.append("downstream_power_out_of_range")

    if us_power is not None and us_power > upstream_power_max:
        reason_codes.append("upstream_power_high")

    if t4_timeouts_total > 0:
        reason_codes.append("t4_timeouts_detected")

    if ofdm_rate > 5000:
        reason_codes.append("ofdm_error_rate_high")

    if t3_rate > 10:
        reason_codes.append("t3_timeout_rate_high")

    return {
        "reason_codes": reason_codes,
        "downstream_locked_channels": ds_locked,
        "downstream_total_channels": ds_total,
        "downstream_snr_min": ds_snr,
        "downstream_power_avg": ds_power,
        "upstream_power_avg": us_power,
        "t3_timeouts_total": t3_timeouts_total,
        "t3_timeouts_per_hour": round(t3_rate, 2),
        "t4_timeouts_total": t4_timeouts_total,
        "ofdm_uncorrected_errors_total": ofdm_uncorrected_total,
        "ofdm_uncorrected_errors_per_hour": round(ofdm_rate, 2),
    }


def has_cable_issue(
    data,
    thresholds: Mapping[str, float] | None = None,
) -> bool:
    """Return whether the DOCSIS measurements indicate a cable issue."""
    analysis = analyze_cable_issue(data, thresholds)
    return bool(analysis["reason_codes"])


@dataclass(frozen=True, kw_only=True)
class ZiggoModemBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict], bool]
    required_endpoints: frozenset[str] = frozenset()


BINARY_SENSORS = (
    ZiggoModemBinarySensorDescription(
        key="internet_access",
        name="Internettoegang",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        required_endpoints=frozenset({ENDPOINT_STATE}),
        value_fn=lambda d: internet_access_allowed(d),
    ),
    ZiggoModemBinarySensorDescription(
        key="cable_issue",
        name="Kabelprobleem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_endpoints=frozenset(
            {
                ENDPOINT_STATE,
                ENDPOINT_DOWNSTREAM,
                ENDPOINT_UPSTREAM,
            }
        ),
        value_fn=lambda d: has_cable_issue(d),
    ),
    ZiggoModemBinarySensorDescription(
        key="internet_outage",
        name="Internet Storing",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_endpoints=frozenset({ENDPOINT_STATE}),
        value_fn=lambda d: internet_outage(d),
    ),
    ZiggoModemBinarySensorDescription(
        key="upstream_timeouts",
        name="Upstream Timeouts Aanwezig",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_endpoints=frozenset({ENDPOINT_UPSTREAM}),
        value_fn=lambda d: sumv(get_us_channels(d), "t4Timeout") > 0
        or sumv(get_us_channels(d), "t3Timeout") > 5
    ),
)


async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host = entry.options.get(CONF_HOST, entry.data[CONF_HOST])

    async_add_entities(
        ZiggoModemBinarySensor(coordinator, entry.entry_id, host, desc)
        for desc in BINARY_SENSORS
    )


class ZiggoModemBinarySensor(ZiggoModemBaseEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id, host, description):
        super().__init__(coordinator, entry_id, host)
        self.entity_description = description
        self._translation_key = f"binary_sensor.{description.key}.name"
        self._attr_name = coordinator.translate(
            f"binary_sensor.{description.key}.name"
        )
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def is_on(self):
        try:
            if self.entity_description.key == "cable_issue":
                return has_cable_issue(
                    self.coordinator.data,
                    self.coordinator.signal_thresholds,
                )
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception:
            return False

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return details explaining why a cable issue is active."""
        if self.entity_description.key != "cable_issue":
            return None

        try:
            analysis = analyze_cable_issue(
                self.coordinator.data,
                self.coordinator.signal_thresholds,
            )
        except Exception:
            return None

        reason_codes = analysis["reason_codes"]
        return {
            **analysis,
            "reasons": [
                self.coordinator.translate(f"cable_issue.reason.{reason_code}")
                for reason_code in reason_codes
            ],
        }
