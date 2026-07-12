from __future__ import annotations

from .const import DEFAULT_LANGUAGE, LANGUAGE_EN, LANGUAGE_NL, LANGUAGE_OPTIONS


TRANSLATIONS = {
    LANGUAGE_NL: {
        "language.nl": "Nederlands",
        "language.en": "Engels",
        "api_status.paused": "Gepauzeerd",
        "api_status.ok": "OK",
        "api_status.temporary_errors": "Tijdelijke fouten",
        "api_status.unstable": "Instabiel",
        "signal_quality.good": "Goed",
        "signal_quality.moderate": "Matig",
        "signal_quality.bad": "Slecht",
        "signal_quality.reason.downstream_unlocked": (
            "Niet alle downstream kanalen zijn gelocked"
        ),
        "signal_quality.reason.downstream_power_high": (
            "Downstream power sterk afwijkend"
        ),
        "signal_quality.reason.downstream_power_warning": (
            "Downstream power licht afwijkend"
        ),
        "signal_quality.reason.downstream_snr_bad": "Downstream SNR te laag",
        "signal_quality.reason.downstream_snr_low": "Downstream SNR verlaagd",
        "signal_quality.reason.downstream_snr_warning": (
            "Downstream SNR iets lager dan ideaal"
        ),
        "signal_quality.reason.upstream_power_bad": "Upstream power te hoog",
        "signal_quality.reason.upstream_power_high": "Upstream power verhoogd",
        "signal_quality.reason.upstream_power_warning": (
            "Upstream power licht verhoogd"
        ),
        "signal_quality.reason.ofdm_errors_bad": (
            "Veel OFDM uncorrected errors per uur"
        ),
        "signal_quality.reason.ofdm_errors_high": (
            "Verhoogde OFDM uncorrected errors per uur"
        ),
        "signal_quality.reason.ofdm_errors_warning": (
            "Lichte OFDM erroractiviteit per uur"
        ),
        "signal_quality.reason.scqam_errors_high": (
            "Verhoogde SC-QAM uncorrected errors per uur"
        ),
        "signal_quality.reason.scqam_errors_warning": (
            "Lichte SC-QAM erroractiviteit per uur"
        ),
        "signal_quality.reason.t3_timeouts_high": "Meerdere T3 timeouts per uur",
        "signal_quality.reason.t3_timeouts_warning": (
            "T3 timeout(s) per uur aanwezig"
        ),
        "signal_quality.reason.normal": (
            "Signaalwaarden vallen binnen normale marges"
        ),
        "signal_quality.advice.none": "Geen actie nodig",
        "signal_quality.advice.watch": (
            "Controleer coaxverbindingen en houd fouttellers in de gaten"
        ),
        "signal_quality.advice.contact": (
            "Controleer splitter, coaxkabel en wandcontactdoos "
            "of neem contact op met de provider"
        ),
        "signal_quality.explanation.good": (
            "DOCSIS signaalwaarden vallen binnen normale marges."
        ),
        "signal_quality.explanation.moderate": (
            "Er zijn afwijkingen zichtbaar in de DOCSIS signaalwaarden, "
            "maar de verbinding kan nog stabiel functioneren."
        ),
        "signal_quality.explanation.bad": (
            "Er zijn duidelijke afwijkingen zichtbaar die relevant kunnen zijn "
            "bij storingen, uitval of instabiliteit."
        ),
        "signal_quality.note": (
            "Dit is een indicatie van DOCSIS signaalkwaliteit en niet van de "
            "totale internetervaring"
        ),
        "line_stability.stable": "Stabiel",
        "line_stability.variable": "Licht wisselend",
        "line_stability.unstable": "Instabiel",
        "issue.provider": "Mogelijke provider-/CMTS-storing",
        "issue.channel": "Mogelijk kanaalprobleem",
        "issue.coax": "Mogelijk coaxprobleem",
        "issue.noise": "Mogelijke instraling / ruis",
        "issue.none": "Geen duidelijke storing",
        "sensor.status.name": "Modem Status",
        "sensor.uptime.name": "Uptime",
        "sensor.signal_quality.name": "Signaalkwaliteit",
        "sensor.signal_quality_explanation.name": "Signaalkwaliteit Uitleg",
        "sensor.signal_quality_advice.name": "Signaalkwaliteit Advies",
        "sensor.software.name": "Software Status",
        "sensor.ds_channels.name": "Downstream Kanalen",
        "sensor.ds_locked.name": "Downstream Gelocked",
        "sensor.ds_power.name": "Downstream Power",
        "sensor.ds_snr.name": "Downstream SNR",
        "sensor.ds_uncorrected_scqam.name": "DS Errors SC-QAM",
        "sensor.ds_uncorrected_ofdm.name": "DS Errors OFDM",
        "sensor.ofdm_errors_rate.name": "OFDM Errors per uur",
        "sensor.scqam_errors_rate.name": "SC-QAM Errors per uur",
        "sensor.t3_timeouts_rate.name": "T3 Timeouts per uur",
        "sensor.ofdm_errors_delta_rate.name": "OFDM Errors actueel per uur",
        "sensor.scqam_errors_delta_rate.name": "SC-QAM Errors actueel per uur",
        "sensor.t3_timeouts_delta_rate.name": "T3 Timeouts actueel per uur",
        "sensor.us_channels.name": "Upstream Kanalen",
        "sensor.us_power.name": "Upstream Power",
        "sensor.us_t3.name": "Upstream T3 Timeouts",
        "sensor.ds_rate.name": "Download Profiel",
        "sensor.us_rate.name": "Upload Profiel",
        "sensor.api_status.name": "API Status",
        "sensor.last_successful_update.name": "Laatste succesvolle update",
        "sensor.line_stability.name": "Lijnstabiliteit",
        "sensor.issue_classification.name": "Storingsclassificatie",
        "binary_sensor.internet_access.name": "Internettoegang",
        "binary_sensor.cable_issue.name": "Kabelprobleem",
        "binary_sensor.internet_outage.name": "Internet Storing",
        "binary_sensor.upstream_timeouts.name": "Upstream Timeouts Aanwezig",
        "button.release_session.name": "Sessie Vrijgeven",
        "button.reboot.name": "Modem Herstarten",
        "switch.pause.name": "Integratie pauzeren",
        "switch.verbose_diagnostics.name": "Uitgebreide diagnostiek",
    },
    LANGUAGE_EN: {
        "language.nl": "Dutch",
        "language.en": "English",
        "api_status.paused": "Paused",
        "api_status.ok": "OK",
        "api_status.temporary_errors": "Temporary errors",
        "api_status.unstable": "Unstable",
        "signal_quality.good": "Good",
        "signal_quality.moderate": "Moderate",
        "signal_quality.bad": "Poor",
        "signal_quality.reason.downstream_unlocked": (
            "Not all downstream channels are locked"
        ),
        "signal_quality.reason.downstream_power_high": (
            "Downstream power is far outside the normal range"
        ),
        "signal_quality.reason.downstream_power_warning": (
            "Downstream power is slightly outside the normal range"
        ),
        "signal_quality.reason.downstream_snr_bad": "Downstream SNR is too low",
        "signal_quality.reason.downstream_snr_low": "Downstream SNR is reduced",
        "signal_quality.reason.downstream_snr_warning": (
            "Downstream SNR is slightly below ideal"
        ),
        "signal_quality.reason.upstream_power_bad": "Upstream power is too high",
        "signal_quality.reason.upstream_power_high": "Upstream power is elevated",
        "signal_quality.reason.upstream_power_warning": (
            "Upstream power is slightly elevated"
        ),
        "signal_quality.reason.ofdm_errors_bad": (
            "Many OFDM uncorrected errors per hour"
        ),
        "signal_quality.reason.ofdm_errors_high": (
            "Elevated OFDM uncorrected errors per hour"
        ),
        "signal_quality.reason.ofdm_errors_warning": (
            "Light OFDM error activity per hour"
        ),
        "signal_quality.reason.scqam_errors_high": (
            "Elevated SC-QAM uncorrected errors per hour"
        ),
        "signal_quality.reason.scqam_errors_warning": (
            "Light SC-QAM error activity per hour"
        ),
        "signal_quality.reason.t3_timeouts_high": "Multiple T3 timeouts per hour",
        "signal_quality.reason.t3_timeouts_warning": (
            "T3 timeout(s) present per hour"
        ),
        "signal_quality.reason.normal": "Signal values are within normal ranges",
        "signal_quality.advice.none": "No action needed",
        "signal_quality.advice.watch": (
            "Check coax connections and keep an eye on error counters"
        ),
        "signal_quality.advice.contact": (
            "Check splitter, coax cable and wall outlet, or contact the provider"
        ),
        "signal_quality.explanation.good": (
            "DOCSIS signal values are within normal ranges."
        ),
        "signal_quality.explanation.moderate": (
            "The DOCSIS signal values show deviations, but the connection may "
            "still function stably."
        ),
        "signal_quality.explanation.bad": (
            "Clear deviations are visible that may be relevant during outages, "
            "dropouts or instability."
        ),
        "signal_quality.note": (
            "This is an indication of DOCSIS signal quality, not of the total "
            "internet experience"
        ),
        "line_stability.stable": "Stable",
        "line_stability.variable": "Slightly unstable",
        "line_stability.unstable": "Unstable",
        "issue.provider": "Possible provider/CMTS issue",
        "issue.channel": "Possible channel issue",
        "issue.coax": "Possible coax issue",
        "issue.noise": "Possible ingress/noise",
        "issue.none": "No clear issue",
        "sensor.status.name": "Modem Status",
        "sensor.uptime.name": "Uptime",
        "sensor.signal_quality.name": "Signal Quality",
        "sensor.signal_quality_explanation.name": "Signal Quality Explanation",
        "sensor.signal_quality_advice.name": "Signal Quality Advice",
        "sensor.software.name": "Software Status",
        "sensor.ds_channels.name": "Downstream Channels",
        "sensor.ds_locked.name": "Locked Downstream Channels",
        "sensor.ds_power.name": "Downstream Power",
        "sensor.ds_snr.name": "Downstream SNR",
        "sensor.ds_uncorrected_scqam.name": "DS Errors SC-QAM",
        "sensor.ds_uncorrected_ofdm.name": "DS Errors OFDM",
        "sensor.ofdm_errors_rate.name": "OFDM Errors per hour",
        "sensor.scqam_errors_rate.name": "SC-QAM Errors per hour",
        "sensor.t3_timeouts_rate.name": "T3 Timeouts per hour",
        "sensor.ofdm_errors_delta_rate.name": "Current OFDM Errors per hour",
        "sensor.scqam_errors_delta_rate.name": "Current SC-QAM Errors per hour",
        "sensor.t3_timeouts_delta_rate.name": "Current T3 Timeouts per hour",
        "sensor.us_channels.name": "Upstream Channels",
        "sensor.us_power.name": "Upstream Power",
        "sensor.us_t3.name": "Upstream T3 Timeouts",
        "sensor.ds_rate.name": "Download Profile",
        "sensor.us_rate.name": "Upload Profile",
        "sensor.api_status.name": "API Status",
        "sensor.last_successful_update.name": "Last successful update",
        "sensor.line_stability.name": "Line Stability",
        "sensor.issue_classification.name": "Issue Classification",
        "binary_sensor.internet_access.name": "Internet Access",
        "binary_sensor.cable_issue.name": "Cable Issue",
        "binary_sensor.internet_outage.name": "Internet Outage",
        "binary_sensor.upstream_timeouts.name": "Upstream Timeouts Present",
        "button.release_session.name": "Release Session",
        "button.reboot.name": "Reboot Modem",
        "switch.pause.name": "Pause Integration",
        "switch.verbose_diagnostics.name": "Verbose Diagnostics",
    },
}


def normalize_language(language: str | None) -> str:
    """Return a supported language code."""
    if language in LANGUAGE_OPTIONS:
        return language
    return DEFAULT_LANGUAGE


def translate(language: str | None, key: str) -> str:
    """Translate a key for the selected integration language."""
    normalized = normalize_language(language)
    fallback = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    return TRANSLATIONS[normalized].get(key, fallback)
