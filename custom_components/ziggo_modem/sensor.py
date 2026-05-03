from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
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

    total_minutes = int(seconds) // 60

    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}u")
    parts.append(f"{minutes}m")

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


def evaluate_signal_quality(data):
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

    uptime = data.get("state", {}).get("cablemodem", {}).get("upTime", 0) or 0
    hours = max(uptime / 3600, 1 / 60)

    ofdm_uncorrected_total = sumv(ds_ofdm, "uncorrectedErrors")
    scqam_uncorrected_total = sumv(ds_scqam, "uncorrectedErrors")
    t3_timeouts_total = sumv(us_all, "t3Timeout")

    ofdm_uncorrected_rate = round(ofdm_uncorrected_total / hours)
    scqam_uncorrected_rate = round(scqam_uncorrected_total / hours)
    t3_timeouts_rate = round(t3_timeouts_total / hours)

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

    if ofdm_uncorrected_rate > 5000:
        score -= 35
        reasons.append("Veel OFDM uncorrected errors per uur")
    elif ofdm_uncorrected_rate > 1000:
        score -= 20
        reasons.append("Verhoogde OFDM uncorrected errors per uur")
    elif ofdm_uncorrected_rate > 100:
        score -= 5
        reasons.append("Lichte OFDM erroractiviteit per uur")

    if scqam_uncorrected_rate > 100:
        score -= 15
        reasons.append("Verhoogde SC-QAM uncorrected errors per uur")
    elif scqam_uncorrected_rate > 10:
        score -= 5
        reasons.append("Lichte SC-QAM erroractiviteit per uur")

    if t3_timeouts_rate > 10:
        score -= 20
        reasons.append("Meerdere T3 timeouts per uur")
    elif t3_timeouts_rate > 2:
        score -= 10
        reasons.append("T3 timeout(s) per uur aanwezig")

    score = max(score, 0)

    if score >= 80:
        status = "Goed"
        advice = "Geen actie nodig"
        explanation = "DOCSIS signaalwaarden vallen binnen normale marges."
    elif score >= 50:
        status = "Matig"
        advice = "Controleer coaxverbindingen en houd fouttellers in de gaten"
        explanation = (
            "Er zijn afwijkingen zichtbaar in de DOCSIS signaalwaarden, "
            "maar de verbinding kan nog stabiel functioneren."
        )
    else:
        status = "Slecht"
        advice = (
            "Controleer splitter, coaxkabel en wandcontactdoos "
            "of neem contact op met de provider"
        )
        explanation = (
            "Er zijn duidelijke afwijkingen zichtbaar die relevant kunnen zijn "
            "bij storingen, uitval of instabiliteit."
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
        "uitleg": explanation,
        "opmerking": (
            "Dit is een indicatie van DOCSIS signaalkwaliteit en niet van de "
            "totale internetervaring"
        ),
        "uptime_hours": round(hours, 2),
        "downstream_power_avg": ds_power,
        "downstream_snr_min": ds_snr,
        "upstream_power_avg": us_power,
        "downstream_locked": ds_locked,
        "downstream_total": ds_total,
        "ofdm_uncorrected_errors_total": ofdm_uncorrected_total,
        "ofdm_uncorrected_errors_per_hour": ofdm_uncorrected_rate,
        "scqam_uncorrected_errors_total": scqam_uncorrected_total,
        "scqam_uncorrected_errors_per_hour": scqam_uncorrected_rate,
        "t3_timeouts_total": t3_timeouts_total,
        "t3_timeouts_per_hour": t3_timeouts_rate,
    }


def evaluate_line_stability(data):
    quality = evaluate_signal_quality(data)

    score = quality["score"]
    t3_rate = quality["t3_timeouts_per_hour"]
    ofdm_rate = quality["ofdm_uncorrected_errors_per_hour"]

    if score >= 80 and t3_rate == 0 and ofdm_rate < 100:
        return "Stabiel"

    if score >= 50:
        return "Licht wisselend"

    return "Instabiel"


def signal_quality(data):
    return evaluate_signal_quality(data)["status"]


def signal_quality_explanation(data):
    return evaluate_signal_quality(data)["uitleg"]


def signal_quality_advice(data):
    return evaluate_signal_quality(data)["advies"]


DELTA_RATE_SENSOR_KEYS = {
    "ofdm_errors_delta_rate",
    "scqam_errors_delta_rate",
    "t3_timeouts_delta_rate",
}


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
        value_fn=lambda d: format_uptime(
            d.get("state", {}).get("cablemodem", {}).get("upTime")
        ),
    ),
    ZiggoModemSensorDescription(
        key="signal_quality",
        name="Signaalkwaliteit",
        value_fn=lambda d: signal_quality(d),
    ),
    ZiggoModemSensorDescription(
        key="signal_quality_explanation",
        name="Signaalkwaliteit Uitleg",
        value_fn=lambda d: signal_quality_explanation(d),
    ),
    ZiggoModemSensorDescription(
        key="signal_quality_advice",
        name="Signaalkwaliteit Advies",
        value_fn=lambda d: signal_quality_advice(d),
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
        key="ofdm_errors_rate",
        name="OFDM Errors per uur",
        native_unit_of_measurement="errors/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: evaluate_signal_quality(d)[
            "ofdm_uncorrected_errors_per_hour"
        ],
    ),
    ZiggoModemSensorDescription(
        key="scqam_errors_rate",
        name="SC-QAM Errors per uur",
        native_unit_of_measurement="errors/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: evaluate_signal_quality(d)[
            "scqam_uncorrected_errors_per_hour"
        ],
    ),
    ZiggoModemSensorDescription(
        key="t3_timeouts_rate",
        name="T3 Timeouts per uur",
        native_unit_of_measurement="timeouts/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: evaluate_signal_quality(d)["t3_timeouts_per_hour"],
    ),
    ZiggoModemSensorDescription(
        key="ofdm_errors_delta_rate",
        name="OFDM Errors actueel per uur",
        native_unit_of_measurement="errors/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: sumv(ofdm_ds(get_ds_channels(d)), "uncorrectedErrors"),
    ),
    ZiggoModemSensorDescription(
        key="scqam_errors_delta_rate",
        name="SC-QAM Errors actueel per uur",
        native_unit_of_measurement="errors/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: sumv(scqam_ds(get_ds_channels(d)), "uncorrectedErrors"),
    ),
    ZiggoModemSensorDescription(
        key="t3_timeouts_delta_rate",
        name="T3 Timeouts actueel per uur",
        native_unit_of_measurement="timeouts/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: sumv(get_us_channels(d), "t3Timeout"),
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
    ZiggoModemSensorDescription(
        key="api_status",
        name="API Status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: None,
    ),
    ZiggoModemSensorDescription(
        key="line_stability",
        name="Lijnstabiliteit",
        value_fn=lambda d: evaluate_line_stability(d),
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
        self._last_delta_total = None
        self._last_delta_time = None
        self._last_data_id = None
        self._cached_native_value = None

    @property
    def native_value(self):
        try:
            if self.entity_description.key == "api_status":
                return self.coordinator.api_status

            value = self.entity_description.value_fn(self.coordinator.data)

            if self.entity_description.key in DELTA_RATE_SENSOR_KEYS:
                return self._calculate_delta_rate(value)

            return value
        except Exception:
            return None

    def _calculate_delta_rate(self, current_total):
        data_id = id(self.coordinator.data)

        if self._last_data_id == data_id:
            return self._cached_native_value

        self._last_data_id = data_id
        now = time.monotonic()

        if current_total is None:
            self._cached_native_value = None
            return None

        if self._last_delta_total is None or self._last_delta_time is None:
            self._last_delta_total = current_total
            self._last_delta_time = now
            self._cached_native_value = 0
            return 0

        elapsed_seconds = now - self._last_delta_time
        delta = current_total - self._last_delta_total

        if delta < 0:
            self._last_delta_total = current_total
            self._last_delta_time = now
            self._cached_native_value = 0
            return 0

        self._last_delta_total = current_total
        self._last_delta_time = now

        if elapsed_seconds <= 0:
            return self._cached_native_value or 0

        rate_per_hour = round(delta / (elapsed_seconds / 3600))
        self._cached_native_value = rate_per_hour
        return rate_per_hour

    @property
    def extra_state_attributes(self):
        if self.entity_description.key == "api_status":
            return {
                "consecutive_failures": self.coordinator.consecutive_failures,
                "max_failures": self.coordinator.max_failures,
                "update_interval_seconds": self.coordinator.update_interval_seconds,
                "paused": self.coordinator.is_paused,
            }

        if self.entity_description.key != "signal_quality":
            return None

        try:
            quality = evaluate_signal_quality(self.coordinator.data)
        except Exception:
            return None

        return {
            "score": quality["score"],
            "reden": quality["reden"],
            "advies": quality["advies"],
            "opmerking": quality["opmerking"],
            "uptime_hours": quality["uptime_hours"],
            "downstream_power_avg": quality["downstream_power_avg"],
            "downstream_snr_min": quality["downstream_snr_min"],
            "upstream_power_avg": quality["upstream_power_avg"],
            "downstream_locked": quality["downstream_locked"],
            "downstream_total": quality["downstream_total"],
            "ofdm_uncorrected_errors_total": quality["ofdm_uncorrected_errors_total"],
            "ofdm_uncorrected_errors_per_hour": quality[
                "ofdm_uncorrected_errors_per_hour"
            ],
            "scqam_uncorrected_errors_total": quality["scqam_uncorrected_errors_total"],
            "scqam_uncorrected_errors_per_hour": quality[
                "scqam_uncorrected_errors_per_hour"
            ],
            "t3_timeouts_total": quality["t3_timeouts_total"],
            "t3_timeouts_per_hour": quality["t3_timeouts_per_hour"],
        }
