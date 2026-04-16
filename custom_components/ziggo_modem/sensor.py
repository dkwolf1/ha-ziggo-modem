from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN
from .entity import ZiggoModemBaseEntity


# =========================
# Helpers
# =========================

def format_uptime(seconds):
    if seconds is None:
        return None
    s = int(seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h or d:
        parts.append(f"{h}u")
    if m or h or d:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


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


def mbit(val):
    return round(val / 1_000_000, 1) if val else None


def first_serviceflow_rate(data, direction):
    for flow in data.get("serviceflows", {}).get("serviceFlows", []):
        sf = flow.get("serviceFlow", {})
        if sf.get("direction") == direction:
            return sf.get("maxTrafficRate")
    return None


def cable_quality(data):
    ds = scqam_ds(get_ds_channels(data))
    us = scqam_us(get_us_channels(data))
    ds_all = get_ds_channels(data)

    ds_snr = minv(ds, "snr")
    ds_power = avg(ds, "power")
    us_power = avg(us, "power")
    ds_locked = locked(ds_all)
    ds_total = len(ds_all)
    ofdm_uncorrected = sumv(ofdm_ds(ds_all), "uncorrectedErrors")

    if ds_total and ds_locked < ds_total:
        return "Slecht"

    if ds_snr is not None and ds_snr < 34:
        return "Slecht"

    if ds_power is not None and (ds_power < -12 or ds_power > 12):
        return "Slecht"

    if us_power is not None and us_power > 52:
        return "Slecht"

    if ofdm_uncorrected > 5000:
        return "Slecht"

    if ds_snr is not None and ds_snr < 38:
        return "Matig"

    if ds_power is not None and (ds_power < -8 or ds_power > 10):
        return "Matig"

    if us_power is not None and us_power > 50:
        return "Matig"

    if ofdm_uncorrected > 1000:
        return "Matig"

    return "Goed"


# =========================
# Sensor definitions
# =========================

@dataclass(frozen=True, kw_only=True)
class ZiggoModemSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS = (
    ZiggoModemSensorDescription(
        key="status",
        name="Modem Status",
        value_fn=lambda d: d["state"]["cablemodem"]["status"],
    ),
    ZiggoModemSensorDescription(
        key="uptime",
        name="Uptime",
        value_fn=lambda d: format_uptime(d["state"]["cablemodem"]["upTime"]),
    ),
    ZiggoModemSensorDescription(
        key="quality",
        name="Kabelkwaliteit",
        value_fn=lambda d: cable_quality(d),
    ),
    ZiggoModemSensorDescription(
        key="software",
        name="Software Status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d["softwareupdate"]["softwareUpdate"]["status"],
    ),
    ZiggoModemSensorDescription(
        key="ds_channels",
        name="Downstream Kanalen",
        value_fn=lambda d: len(get_ds_channels(d)),
    ),
    ZiggoModemSensorDescription(
        key="ds_locked",
        name="Downstream Gelocked",
        value_fn=lambda d: locked(get_ds_channels(d)),
    ),
    ZiggoModemSensorDescription(
        key="ds_power",
        name="Downstream Power",
        native_unit_of_measurement="dBmV",
        value_fn=lambda d: avg(scqam_ds(get_ds_channels(d)), "power"),
    ),
    ZiggoModemSensorDescription(
        key="ds_snr",
        name="Downstream SNR",
        native_unit_of_measurement="dB",
        value_fn=lambda d: minv(scqam_ds(get_ds_channels(d)), "snr"),
    ),
    ZiggoModemSensorDescription(
        key="ds_uncorrected_scqam",
        name="DS Errors SC-QAM",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: sumv(scqam_ds(get_ds_channels(d)), "uncorrectedErrors"),
    ),
    ZiggoModemSensorDescription(
        key="ds_uncorrected_ofdm",
        name="DS Errors OFDM",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: sumv(ofdm_ds(get_ds_channels(d)), "uncorrectedErrors"),
    ),
    ZiggoModemSensorDescription(
        key="us_channels",
        name="Upstream Kanalen",
        value_fn=lambda d: len(get_us_channels(d)),
    ),
    ZiggoModemSensorDescription(
        key="us_power",
        name="Upstream Power",
        native_unit_of_measurement="dBmV",
        value_fn=lambda d: avg(scqam_us(get_us_channels(d)), "power"),
    ),
    ZiggoModemSensorDescription(
        key="us_t3",
        name="Upstream T3 Timeouts",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: sumv(get_us_channels(d), "t3Timeout"),
    ),
    ZiggoModemSensorDescription(
        key="ds_rate",
        name="Download Profiel",
        native_unit_of_measurement="Mbit/s",
        value_fn=lambda d: mbit(first_serviceflow_rate(d, "downstream")),
    ),
    ZiggoModemSensorDescription(
        key="us_rate",
        name="Upload Profiel",
        native_unit_of_measurement="Mbit/s",
        value_fn=lambda d: mbit(first_serviceflow_rate(d, "upstream")),
    ),
)


async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host = entry.options.get(CONF_HOST, entry.data[CONF_HOST])

    async_add_entities(
        ZiggoModemSensor(coordinator, entry.entry_id, host, desc)
        for desc in SENSORS
    )


class ZiggoModemSensor(ZiggoModemBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, host, description):
        super().__init__(coordinator, entry_id, host)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self):
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception:
            return None
