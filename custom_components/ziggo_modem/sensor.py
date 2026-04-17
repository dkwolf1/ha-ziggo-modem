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


def evaluate_cable_quality(data):
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
    ofdm_uncorrected = sumv(ds_ofdm, "uncorrectedErrors")
    scqam_uncorrected = sumv(ds_scqam, "uncorrectedErrors")
    t3_timeouts = sumv(us_all, "t3Timeout")

    score = 100
    reasons = []

    if ds_total and ds_locked < ds_total:
        score -= 35
        reasons.append("Niet alle downstream kanalen zijn gelocked")

    if ds_power is not None:
        if ds_power < -10 or ds_power > 10:
            score -= 25
            reasons.append("Downstream power sterk afwijkend")
        elif ds_power < -8 or ds_power > 8:
            score -= 10
            reasons.append("Downstream power licht afwijkend")

    if ds_snr is not None:
        if ds_snr < 34:
            score -= 40
            reasons.append("Downstream SNR te laag")
        elif ds_snr < 37:
            score -= 25
            reasons.append("Downstream SNR verlaagd")
        elif ds_snr < 40:
            score -= 10
            reasons.append("Downstream SNR iets lager dan ideaal")

    if us_power is not None:
        if us_power > 52:
            score -= 35
            reasons.append("Upstream power te hoog")
        elif us_power > 50:
            score -= 20
            reasons.append("Upstream power verhoogd")
        elif us_power > 48:
            score -= 10
            reasons.append("Upstream power licht verhoogd")

    if ofdm_uncorrected > 5000:
        score -= 35
        reasons.append("Veel OFDM uncorrected errors")
    elif ofdm_uncorrected > 1000:
        score -= 20
        reasons.append("Verhoogde OFDM uncorrected errors")
    elif ofdm_uncorrected > 10:
        score -= 5
        reasons.append("Lichte OFDM erroractiviteit")

    if t3_timeouts > 2:
        score -= 20
        reasons.append("Meerdere T3 timeouts")
    elif t3_timeouts > 0:
        score -= 10
        reasons.append("T3 timeout(s) aanwezig")

    score = max(score, 0)

    if score >= 80:
        status = "Goed"
        advice = "Geen actie nodig"
    elif score >= 50:
        status = "Matig"
        advice = "Controleer coaxverbindingen en houd fouttellers in de gaten"
    else:
        status = "Slecht"
        advice = (
            "Controleer splitter, coaxkabel en wandcontactdoos "
            "of neem contact op met de provider"
        )

    reason = (
        ", ".join(reasons)
        if reasons
        else "Signaalwaarden vallen binnen normale marges"
    )

    return {
        "status": status,
        "score": score,
        "reden": reason,
        "advies": advice,
        "downstream_power_avg": ds_power,
        "downstream_snr_min": ds_snr,
        "upstream_power_avg": us_power,
        "downstream_locked": ds_locked,
        "downstream_total": ds_total,
        "ofdm_uncorrected_errors": ofdm_uncorrected,
        "scqam_uncorrected_errors": scqam_uncorrected,
        "t3_timeouts": t3_timeouts,
    }


def cable_quality(data):
    return evaluate_cable_quality(data)["status"]


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

    @property
    def extra_state_attributes(self):
        if self.entity_description.key != "quality":
            return None

        try:
            quality = evaluate_cable_quality(self.coordinator.data)
        except Exception:
            return None

        return {
            "score": quality["score"],
            "reden": quality["reden"],
            "advies": quality["advies"],
            "downstream_power_avg": quality["downstream_power_avg"],
            "downstream_snr_min": quality["downstream_snr_min"],
            "upstream_power_avg": quality["upstream_power_avg"],
            "downstream_locked": quality["downstream_locked"],
            "downstream_total": quality["downstream_total"],
            "ofdm_uncorrected_errors": quality["ofdm_uncorrected_errors"],
            "scqam_uncorrected_errors": quality["scqam_uncorrected_errors"],
            "t3_timeouts": quality["t3_timeouts"],
        }
