from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN
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


def has_cable_issue(data):
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
        return True
    if ds_snr is not None and ds_snr < 34:
        return True
    if ds_power is not None and (ds_power < -12 or ds_power > 12):
        return True
    if us_power is not None and us_power > 52:
        return True
    if ofdm_uncorrected > 5000:
        return True

    return False


@dataclass(frozen=True, kw_only=True)
class ZiggoModemBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict], bool]


BINARY_SENSORS = (
    ZiggoModemBinarySensorDescription(
        key="internet_access",
        name="Internet Toegang",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda d: d["state"]["cablemodem"]["accessAllowed"],
    ),
    ZiggoModemBinarySensorDescription(
        key="cable_issue",
        name="Kabelprobleem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: has_cable_issue(d),
    ),
    ZiggoModemBinarySensorDescription(
        key="internet_outage",
        name="Internet Storing",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: not d["state"]["cablemodem"]["accessAllowed"],
    ),
    ZiggoModemBinarySensorDescription(
        key="upstream_timeouts",
        name="Upstream Timeouts Aanwezig",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: sumv(get_us_channels(d), "t3Timeout") > 0
        or sumv(get_us_channels(d), "t4Timeout") > 0,
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
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def is_on(self):
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception:
            return False
