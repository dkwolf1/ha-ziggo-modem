# Ziggo Modem: readings and troubleshooting

[Wiki home](https://github.com/dkwolf1/ha-ziggo-modem/wiki/Home) | [Nederlands](https://github.com/dkwolf1/ha-ziggo-modem/wiki/Nederlands)

## What the integration knows

Home Assistant logs in to the **local modem API** over HTTPS and polls six
endpoints: `state`, `downstream`, `primary_downstream`, `upstream`,
`serviceflows` and `softwareupdate`. The default interval is 60 seconds
(configurable from 5 to 3600 seconds). It does not use Ziggo SmartWifi Web.

The integration reads modem-reported DOCSIS status, uptime, channel lock,
power, SNR, error counters, timeouts, provisioned service-flow rates and the
modem's `accessAllowed` value. Device information such as model and firmware
is shown when the modem supplies it. A fallback model name is not proof of a
specific model.

The integration **does not** ping websites, run a speed test, measure latency
or Wi-Fi quality, query Ziggo's network status, or identify a faulty cable,
splitter, wall outlet or street cabinet with certainty. An issue category is a
heuristic, not a confirmed root cause. A healthy score does not guarantee a
good internet experience.

## Start with these three entities

| Entity | Meaning |
| --- | --- |
| **API Status** | Whether local API polling works. Check its `endpoint_status`, `failed_endpoints`, `consecutive_failures` and `last_successful_update` attributes. This is not the internet status. |
| **Signal Quality** | Calculated DOCSIS score and label. Its `reason`, `score` and measurement attributes explain the label. |
| **Issue Classification** | One *possible* cause selected by priority from modem-reported values. It is not an official Ziggo outage report. |

If these disagree, check their source data and timestamps. For example, the
modem API may be reachable while DOCSIS signal quality is poor. Conversely,
the local API may fail even while ordinary internet access still works.

## DOCSIS terms in plain language

- **Downstream** is the path from the cable network to the modem; **upstream** is the path back. These are cable-link directions, not measured download/upload speed.
- **Power (dBmV)** is the signal level reported for a channel. A value outside the configured limits is a clue, not proof of where the fault is located.
- **SNR (dB)** compares signal with noise. The integration uses the lowest reported SC-QAM downstream SNR, so one weak channel can affect the result.
- **Locked channel** means the modem reports that it has synchronized to that DOCSIS channel. A missing lock can reduce the available cable link, but the integration cannot identify the physical cause.
- **Corrected/uncorrected errors** are counters reported by the modem. Uncorrected errors are the ones used in this integration's quality rules. An accumulated total is not the same as a new error burst.
- **T3/T4 timeouts** are modem-reported DOCSIS timing/ranging events. Their presence merits comparison with current connectivity and signal readings; a historical total alone does not prove an ongoing outage.

## Signal Quality and Line Stability

Signal Quality starts at **100 points**. The following penalties are added,
then the result is floored at zero. Default thresholds can be changed under
**Settings > Devices & services > Ziggo Modem > Configure**.

| Reading | Penalty |
| --- | --- |
| At least one reported downstream channel not locked | -35 |
| Average SC-QAM downstream power outside configured minimum/maximum (default -10 to +10 dBmV) | -25 |
| Average SC-QAM downstream power close to a limit (within a warning margin of at most 2 dBmV) | -10 |
| Minimum SC-QAM downstream SNR below configured minimum (default 34 dB) | -40 |
| Minimum SC-QAM downstream SNR from minimum to less than minimum +3 dB | -25 |
| Minimum SC-QAM downstream SNR from minimum +3 to less than minimum +6 dB | -10 |
| Average ATDMA upstream power above configured maximum (default 52 dBmV) | -35 |
| Average ATDMA upstream power above maximum -2 dBmV | -20 |
| Average ATDMA upstream power above maximum -4 dBmV | -10 |
| OFDM uncorrected errors per uptime-hour: >5000 / >1000 / >100 | -35 / -20 / -5 |
| SC-QAM uncorrected errors per uptime-hour: >100 / >10 | -15 / -5 |
| T3 timeouts per uptime-hour: >10 / >2 | -20 / -10 |

Each row with several bands applies **one** penalty, not all penalties in that
row. Score **80-100 = Good**, **50-79 = Moderate**, **0-49 = Poor**. The
Explanation and Advice entities give generic guidance for the resulting band;
the `reason` attribute names the measurements that contributed. Missing
channel values do not trigger their corresponding penalty, so a good score
alone is not evidence that every metric was measured.

**Line Stability** is Stable only if the score is at least 80, the calculated
T3 rate is zero and the calculated OFDM rate is below 100 per uptime-hour. It
is Slightly unstable if the score is at least 50 but the Stable conditions
are not met; otherwise it is Unstable. These are calculated labels, not
continuous packet-loss measurements.

## Issue Classification

Only the **first** matching category below is shown. A later condition can
also be present; inspect Signal Quality and Cable Issue for all active clues.

| Label | Trigger | Interpretation |
| --- | --- | --- |
| Possible provider/CMTS issue | Modem `accessAllowed` explicitly reports false | The modem reports access denied. It does **not** prove a Ziggo-wide outage or identify the CMTS. |
| Possible channel issue | At least one reported downstream channel is not locked | A DOCSIS channel lock problem is visible. |
| Possible coax issue | Average ATDMA upstream power > configured maximum; or T3 rate >10 per uptime-hour; or average SC-QAM downstream power outside configured range; or SC-QAM uncorrected rate >100 per uptime-hour | These measurements may point to a coax/RF-path problem; the physical location is unknown. |
| Possible ingress/noise | Minimum SC-QAM downstream SNR < configured minimum; or OFDM uncorrected rate >5000 per uptime-hour | Noise or interference is plausible, not confirmed. |
| No clear issue | None of the above | No matching rule, **not** a clean bill of health. |

The exact priority in code is: access denied, unlocked channel, high upstream
power, high T3 rate, low downstream SNR, high OFDM error rate, out-of-range
downstream power, high SC-QAM error rate, then no clear issue. For example,
high upstream power can mask low SNR in this *single* label.

## Binary alerts

| Entity | When it turns on |
| --- | --- |
| **Internet Access** | The modem's `accessAllowed` value is recognized as true. This is a modem-reported permission, not a successful external connectivity test. |
| **Internet Outage** | `accessAllowed` is recognized as false. This means the modem reports denied access; it does not independently test internet reachability. |
| **Cable Issue** | At least one rule in the table below matches. Look at `reason_codes`, `reasons` and measurement attributes. |
| **Upstream Timeouts Present** | Total reported T4 timeouts >0, or total T3 timeouts >5. These are modem counters, not necessarily events in the current hour. |

If `accessAllowed` is missing or unrecognized, both Internet Access and
Internet Outage evaluate to off. Do not read that combination as proof of
either working internet or an outage.

**Cable Issue reason codes:**

| `reason_codes` value | Exact rule |
| --- | --- |
| `downstream_channels_unlocked` | Fewer locked than total downstream channels. |
| `downstream_snr_low` | Minimum SC-QAM downstream SNR < configured minimum minus 1 dB. |
| `downstream_power_out_of_range` | Average SC-QAM downstream power < configured minimum minus 2 dBmV, or > maximum plus 2 dBmV. |
| `upstream_power_high` | Average ATDMA upstream power > configured maximum. |
| `t4_timeouts_detected` | Total reported T4 timeouts >0. |
| `ofdm_error_rate_high` | OFDM uncorrected errors / uptime-hours >5000. |
| `t3_timeout_rate_high` | T3 timeouts / uptime-hours >10. |

Cable Issue deliberately uses an extra margin for downstream SNR and power,
so it need not switch on for every Moderate/Poor Signal Quality result.

## Other readings and limits

- **Downstream Power** is the average of reported SC-QAM channel power; **Downstream SNR** is the minimum reported SC-QAM SNR. OFDM channels are not included in these two aggregates. **Upstream Power** averages reported ATDMA channels.
- **Downstream Channels / Locked Downstream Channels / Upstream Channels** count channels reported by the modem; a missing list can look like zero.
- **DS Errors SC-QAM / DS Errors OFDM / Upstream T3 Timeouts** are sums of modem-reported counters. A total can persist until the modem resets its counters; it is not necessarily a new incident.
- **OFDM Errors per hour / SC-QAM Errors per hour / T3 Timeouts per hour** divide total counters by modem uptime (with a one-minute minimum denominator). They are *averages since uptime began*, not the rate during the last hour.
- **Current OFDM Errors per hour / Current SC-QAM Errors per hour / Current T3 Timeouts per hour** calculate the change between successful readings and scale it to an hour. They start at zero, reset to zero when the underlying counter decreases, and are disabled by default in the entity registry. Short polling windows can produce large extrapolated values.
- **Download Profile / Upload Profile** are the first matching service flow's configured `maxTrafficRate`, converted to Mbit/s. They are **not** measured download/upload speed.
- **Modem Status / Software Status** display raw status strings supplied by the modem. Their meaning can vary by firmware. **Uptime** is also modem-reported.
- **Last Modem Restart** is an estimate from current time minus reported uptime. It is not a timestamp returned directly by the modem.

## API failures, availability and history

**API Status** is `OK` when no recent endpoint failures are reported,
`Temporary errors` during recoverable failures, `Unstable` after three
consecutive complete update failures or when a failed endpoint has no usable
cached reading, and `Paused` when polling is intentionally paused. The
`endpoint_status` attribute lists each endpoint as `ok` or `failed` on its
most recent fetch. The `primary_downstream` endpoint is checked but has no
dedicated entity in the current integration.

For an isolated endpoint failure, dependent entities may retain their last
successful value for **less than 10 minutes**; other endpoints can continue
updating. After that, those dependent entities become unavailable. A complete
API failure also retains the previous coordinator data for less than 10
minutes, then entities become unavailable. API Status itself may become
unavailable after a prolonged complete failure, so check the Home Assistant
integration state and logs too. `Paused` means polling was stopped by the
Pause Integration switch; it is not evidence of a modem outage. Authentication
failure triggers a Home Assistant reauthentication flow rather than treating
old data as valid indefinitely.

**Failed Updates** increments on every fully failed poll (all endpoints fail,
or authentication fails). A single failed endpoint does not increment it.
**Connection Interruptions** increments only when a previously reachable
modem becomes completely unreachable; an authentication failure does not count
as a connection interruption. These counters persist across Home Assistant
restarts. **Last successful update** is the latest poll with at least one
successful endpoint; it does not mean *all* endpoint data was refreshed.

## Troubleshooting

1. Check **API Status**, `endpoint_status` and **Last successful update** first. A failed endpoint suggests an API/firmware issue; failing all endpoints may also indicate local reachability, login or modem availability trouble.
2. Check the modem's local IP from the Home Assistant network, not only from another computer. Open `https://<modem-ip>` on the same network. This integration uses `https://<modem-ip>/rest/v1`; an external Ziggo website is not involved.
3. For **Invalid credentials**, use Home Assistant's reauthentication prompt and verify the modem password. Leave the username empty for password-only modems. For a changed IP, use **Reconfigure** instead of removing the integration.
4. For **Cannot connect**, check the local address, routing, modem interface and whether the API responds. **Unknown error** needs logs for diagnosis; it is not a separate cable fault classification.
5. For a cable or signal warning, compare the `reason_codes`, actual readings and configured thresholds. Check accessible coax connectors/splitters. If the signal stays poor or service is affected, contact Ziggo with the readings. Do not treat one stale counter as a fresh failure.
6. For frequent temporary errors, compare the polling interval, endpoint statuses and Home Assistant logs. The **Release Session** button discards the integration's current modem login token and requests a refresh; it does not repair DOCSIS signal. **Reboot Modem** actually requests a modem reboot and interrupts service, so use it deliberately.

Download diagnostics from **Settings > Devices & services > Ziggo Modem >
three-dot menu > Download diagnostics**. It contains settings, endpoint status
and latest modem data with known secret/network fields redacted. **Review it
before posting publicly**. Verbose Diagnostics adds per-channel attributes
to Signal Quality; enable it only while investigating an issue.

## Setup messages

| Message | Meaning |
| --- | --- |
| **Invalid credentials** | The modem rejected login, or login returned no usable token. |
| **Cannot connect to modem** | A modem API/login request failed; check local reachability and the modem interface. |
| **Unknown error** | An unexpected setup error; inspect Home Assistant logs. |
| **Already configured** | The same modem address is already present as an integration entry. |

This page describes the current repository implementation, primarily tested
on Sagemcom Ziggo modems. Firmware differences can change API fields and OFDM
interpretation.
