from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DEFAULT_LANGUAGE, DOMAIN, LANGUAGE_NL
from .entity import ZiggoModemBaseEntity
from .i18n import translate


# =========================
# Helpers
# =========================


def format_uptime(seconds, language=DEFAULT_LANGUAGE):
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
        parts.append(f"{hours}u" if language == LANGUAGE_NL else f"{hours}h")
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


def summarize_channel(channel):
    """Return a compact diagnostic summary for a DOCSIS channel."""
    return {
        "id": channel.get("channelId") or channel.get("id"),
        "type": channel.get("channelType"),
        "locked": channel.get("lockStatus"),
        "frequency": channel.get("frequency"),
        "power": channel.get("power"),
        "snr": channel.get("snr"),
        "modulation": channel.get("modulation"),
        "corrected_errors": channel.get("correctedErrors"),
        "uncorrected_errors": channel.get("uncorrectedErrors"),
        "t3_timeouts": channel.get("t3Timeout"),
        "t4_timeouts": channel.get("t4Timeout"),
    }


def verbose_diagnostic_attributes(data):
    """Return extra channel diagnostics for advanced troubleshooting."""
    return {
        "downstream_channels": [
            summarize_channel(channel) for channel in get_ds_channels(data)
        ],
        "upstream_channels": [
            summarize_channel(channel) for channel in get_us_channels(data)
        ],
    }


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


def mbit(val):
    return round(val / 1_000_000, 1) if val else None


def first_serviceflow_rate(data, direction):
    for flow in data.get("serviceflows", {}).get("serviceFlows", []):
        sf = flow.get("serviceFlow", {})
        if sf.get("direction") == direction:
            return sf.get("maxTrafficRate")
    return None


def evaluate_signal_quality(data, language=DEFAULT_LANGUAGE):
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
        reasons.append(
            translate(language, "signal_quality.reason.downstream_unlocked")
        )

    if ds_power is not None:
        if ds_power < -10 or ds_power > 10:
            score -= 25
            reasons.append(
                translate(language, "signal_quality.reason.downstream_power_high")
            )
        elif ds_power < -8 or ds_power > 8:
            score -= 10
            reasons.append(
                translate(language, "signal_quality.reason.downstream_power_warning")
            )

    if ds_snr is not None:
        if ds_snr < 34:
            score -= 40
            reasons.append(
                translate(language, "signal_quality.reason.downstream_snr_bad")
            )
        elif ds_snr < 37:
            score -= 25
            reasons.append(
                translate(language, "signal_quality.reason.downstream_snr_low")
            )
        elif ds_snr < 40:
            score -= 10
            reasons.append(
                translate(language, "signal_quality.reason.downstream_snr_warning")
            )

    if us_power is not None:
        if us_power > 52:
            score -= 35
            reasons.append(
                translate(language, "signal_quality.reason.upstream_power_bad")
            )
        elif us_power > 50:
            score -= 20
            reasons.append(
                translate(language, "signal_quality.reason.upstream_power_high")
            )
        elif us_power > 48:
            score -= 10
            reasons.append(
                translate(language, "signal_quality.reason.upstream_power_warning")
            )

    if ofdm_uncorrected_rate > 5000:
        score -= 35
        reasons.append(translate(language, "signal_quality.reason.ofdm_errors_bad"))
    elif ofdm_uncorrected_rate > 1000:
        score -= 20
        reasons.append(translate(language, "signal_quality.reason.ofdm_errors_high"))
    elif ofdm_uncorrected_rate > 100:
        score -= 5
        reasons.append(translate(language, "signal_quality.reason.ofdm_errors_warning"))

    if scqam_uncorrected_rate > 100:
        score -= 15
        reasons.append(translate(language, "signal_quality.reason.scqam_errors_high"))
    elif scqam_uncorrected_rate > 10:
        score -= 5
        reasons.append(
            translate(language, "signal_quality.reason.scqam_errors_warning")
        )

    if t3_timeouts_rate > 10:
        score -= 20
        reasons.append(translate(language, "signal_quality.reason.t3_timeouts_high"))
    elif t3_timeouts_rate > 2:
        score -= 10
        reasons.append(translate(language, "signal_quality.reason.t3_timeouts_warning"))

    score = max(score, 0)

    if score >= 80:
        status = translate(language, "signal_quality.good")
        advice = translate(language, "signal_quality.advice.none")
        explanation = translate(language, "signal_quality.explanation.good")
    elif score >= 50:
        status = translate(language, "signal_quality.moderate")
        advice = translate(language, "signal_quality.advice.watch")
        explanation = translate(language, "signal_quality.explanation.moderate")
    else:
        status = translate(language, "signal_quality.bad")
        advice = translate(language, "signal_quality.advice.contact")
        explanation = translate(language, "signal_quality.explanation.bad")

    reason = (
        ", ".join(reasons)
        if reasons
        else translate(language, "signal_quality.reason.normal")
    )

    return {
        "status": status,
        "score": score,
        "reden": reason,
        "advies": advice,
        "uitleg": explanation,
        "opmerking": translate(language, "signal_quality.note"),
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


def evaluate_line_stability(data, language=DEFAULT_LANGUAGE):
    quality = evaluate_signal_quality(data, language)

    score = quality["score"]
    t3_rate = quality["t3_timeouts_per_hour"]
    ofdm_rate = quality["ofdm_uncorrected_errors_per_hour"]

    if score >= 80 and t3_rate == 0 and ofdm_rate < 100:
        return translate(language, "line_stability.stable")

    if score >= 50:
        return translate(language, "line_stability.variable")

    return translate(language, "line_stability.unstable")


def classify_connection_issue(data, language=DEFAULT_LANGUAGE):
    quality = evaluate_signal_quality(data, language)

    ds_snr = quality["downstream_snr_min"]
    ds_power = quality["downstream_power_avg"]
    us_power = quality["upstream_power_avg"]
    ds_locked = quality["downstream_locked"]
    ds_total = quality["downstream_total"]
    ofdm_rate = quality["ofdm_uncorrected_errors_per_hour"]
    scqam_rate = quality["scqam_uncorrected_errors_per_hour"]
    t3_rate = quality["t3_timeouts_per_hour"]

    access_allowed = data.get("state", {}).get(
        "cablemodem", {}
    ).get("accessAllowed")

    if normalize_access_allowed(access_allowed) is False:
        return translate(language, "issue.provider")

    if ds_total and ds_locked < ds_total:
        return translate(language, "issue.channel")

    if us_power is not None and us_power > 52:
        return translate(language, "issue.coax")

    if t3_rate > 10:
        return translate(language, "issue.coax")

    if ds_snr is not None and ds_snr < 34:
        return translate(language, "issue.noise")

    if ofdm_rate > 5000:
        return translate(language, "issue.noise")

    if ds_power is not None and (ds_power < -10 or ds_power > 10):
        return translate(language, "issue.coax")

    if scqam_rate > 100:
        return translate(language, "issue.coax")

    return translate(language, "issue.none")


def signal_quality(data, language=DEFAULT_LANGUAGE):
    return evaluate_signal_quality(data, language)["status"]


def signal_quality_explanation(data, language=DEFAULT_LANGUAGE):
    return evaluate_signal_quality(data, language)["uitleg"]


def signal_quality_advice(data, language=DEFAULT_LANGUAGE):
    return evaluate_signal_quality(data, language)["advies"]


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
        key="last_successful_update",
        name="Laatste succesvolle update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: None,
    ),
    ZiggoModemSensorDescription(
        key="line_stability",
        name="Lijnstabiliteit",
        value_fn=lambda d: evaluate_line_stability(d),
    ),
    ZiggoModemSensorDescription(
        key="issue_classification",
        name="Storingsclassificatie",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: classify_connection_issue(d),
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
        self._translation_key = f"sensor.{description.key}.name"
        self._attr_name = coordinator.translate(f"sensor.{description.key}.name")
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._last_delta_total = None
        self._last_delta_time = None
        self._last_data_id = None
        self._cached_native_value = None

    @property
    def native_value(self):
        try:
            language = self.coordinator.language

            if self.entity_description.key == "api_status":
                return self.coordinator.api_status

            if self.entity_description.key == "last_successful_update":
                return self.coordinator.last_successful_update

            if self.entity_description.key == "uptime":
                uptime = self.coordinator.data.get("state", {}).get(
                    "cablemodem", {}
                ).get("upTime")
                return format_uptime(uptime, language)

            if self.entity_description.key == "signal_quality":
                return signal_quality(self.coordinator.data, language)

            if self.entity_description.key == "signal_quality_explanation":
                return signal_quality_explanation(self.coordinator.data, language)

            if self.entity_description.key == "signal_quality_advice":
                return signal_quality_advice(self.coordinator.data, language)

            if self.entity_description.key == "line_stability":
                return evaluate_line_stability(self.coordinator.data, language)

            if self.entity_description.key == "issue_classification":
                return classify_connection_issue(self.coordinator.data, language)

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
            endpoint_status = self.coordinator.endpoint_status

            return {
                "consecutive_failures": self.coordinator.consecutive_failures,
                "max_failures": self.coordinator.max_failures,
                "update_interval_seconds": self.coordinator.update_interval_seconds,
                "paused": self.coordinator.is_paused,
                "verbose_diagnostics": self.coordinator.verbose_diagnostics,
                "language": self.coordinator.language,
                "endpoint_status": endpoint_status,
                "failed_endpoints": [
                    endpoint
                    for endpoint, status in endpoint_status.items()
                    if status == "failed"
                ],
            }

        if self.entity_description.key != "signal_quality":
            return None

        try:
            quality = evaluate_signal_quality(
                self.coordinator.data,
                self.coordinator.language,
            )
        except Exception:
            return None

        language = self.coordinator.language
        text_attributes = (
            {
                "reden": quality["reden"],
                "advies": quality["advies"],
                "opmerking": quality["opmerking"],
            }
            if language == LANGUAGE_NL
            else {
                "reason": quality["reden"],
                "advice": quality["advies"],
                "note": quality["opmerking"],
            }
        )

        attributes = {
            **text_attributes,
            "score": quality["score"],
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

        if self.coordinator.verbose_diagnostics:
            attributes.update(verbose_diagnostic_attributes(self.coordinator.data))

        return attributes
