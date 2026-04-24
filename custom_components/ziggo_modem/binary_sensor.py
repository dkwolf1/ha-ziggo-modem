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
    """Return True only for real DOCSIS signal problems (not minor fluctuations)."""

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

    # 👉 uptime meenemen → alles naar per uur
    uptime = data.get("state", {}).get("cablemodem", {}).get("upTime", 0)
    hours = max(uptime / 3600, 1 / 60)

    ofdm_uncorrected_total = sumv(ds_ofdm, "uncorrectedErrors")
    t3_timeouts_total = sumv(us_all, "t3Timeout")
    t4_timeouts_total = sumv(us_all, "t4Timeout") if us_all else 0

    ofdm_rate = ofdm_uncorrected_total / hours
    t3_rate = t3_timeouts_total / hours

    # =========================
    # Harde problemen
    # =========================

    # Kanalen niet gelocked → altijd fout
    if ds_total and ds_locked < ds_total:
        return True

    # Slechte SNR → echt probleem
    if ds_snr is not None and ds_snr < 33:
        return True

    # Extreme power afwijking
    if ds_power is not None and (ds_power < -12 or ds_power > 12):
        return True

    # Upstream te hoog → modem moet schreeuwen
    if us_power is not None and us_power > 52:
        return True

    # T4 timeouts → altijd fout
    if t4_timeouts_total > 0:
        return True

    # =========================
    # Zwaardere instabiliteit (rate-based)
    # =========================

    # Veel OFDM errors per uur → probleem
    if ofdm_rate > 5000:
        return True

    # Structurele T3 timeouts → probleem
    if t3_rate > 10:
        return True

    # =========================
    # Alles daaronder = geen probleem
    # =========================

    return False


@dataclass(frozen=True, kw_only=True)
class ZiggoModemBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict], bool]


BINARY_SENSORS = (
    ZiggoModemBinarySensorDescription(
        key="internet_access",
        name="Internettoegang",
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
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def is_on(self):
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception:
            return False
