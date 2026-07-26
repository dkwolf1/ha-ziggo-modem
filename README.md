# Ziggo Modem

[![GitHub Release](https://img.shields.io/github/v/release/dkwolf1/ha-ziggo-modem?style=for-the-badge)](https://github.com/dkwolf1/ha-ziggo-modem/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/dkwolf1/ha-ziggo-modem?style=for-the-badge)](https://github.com/dkwolf1/ha-ziggo-modem/commits/main)
[![License](https://img.shields.io/github/license/dkwolf1/ha-ziggo-modem?style=for-the-badge)](LICENSE)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz)

[![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen?style=for-the-badge)]()
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.4%2B-blue?style=for-the-badge)](https://www.home-assistant.io/)

---

## English

Local Home Assistant integration for Ziggo cable modems (Sagemcom).

This integration gives insight into your DOCSIS connection, including signal
quality, stability, error counters and network status. It works locally and
does not use SmartWifi Web or any external Ziggo website.

### Features

- Modem status and uptime
- Modem model, firmware, hardware, serial number and MAC address in device info
- Downloadable, privacy-redacted Home Assistant diagnostics
- Configurable DOCSIS signal thresholds
- Persistent connection interruption and failed update history
- Downstream signal analysis (power, SNR, errors)
- Upstream monitoring (power, timeouts)
- SC-QAM and OFDM error analysis
- Download and upload profile detection
- Last successful update timestamp
- Per-endpoint API status diagnostics
- Optional verbose diagnostics with channel details

### Installation

#### HACS (recommended)

1. Go to **HACS > Integrations**.
2. Click **three dots > Custom repositories**.
3. Add this repository.
4. Select category **Integration**.
5. Install **Ziggo Modem**.
6. Restart Home Assistant.

#### Manual

1. Copy `custom_components/ziggo_modem` to your Home Assistant configuration
   directory.
2. Restart Home Assistant.

### Configuration

The integration is configured through the Home Assistant UI:

**Settings > Devices & services > Add integration > Ziggo Modem**

Enter:

- IP address (default: `192.168.100.1`)
- Username (optional; leave empty for password-only modems)
- Password
- Language: `Nederlands` or `English`

The integration requires direct local access to the modem interface/API. The
local modem IP must be reachable from Home Assistant. SmartWifi Web/cloud login
is not used.

### Options

Open **Settings > Devices & services > Ziggo Modem > Configure** to change:

- Minimum downstream power (default: `-10 dBmV`)
- Maximum downstream power (default: `10 dBmV`)
- Minimum downstream SNR (default: `34 dB`)
- Maximum upstream power (default: `52 dBmV`)

These thresholds affect signal quality, issue classification and the cable
issue sensor. The defaults preserve the original integration behavior. The
cable issue sensor keeps an additional safety margin to avoid triggering on
minor fluctuations.

### Sensors

General:

- Modem status
- Uptime
- Signal quality
- Signal quality explanation
- Signal quality advice
- Line stability
- API status
- Last successful update
- Connection interruptions
- Failed updates
- Last modem restart
- Issue classification

Downstream:

- Downstream power (dBmV)
- Downstream SNR (dB)
- Channel count
- Locked channels
- SC-QAM / OFDM errors

Upstream:

- Upstream power (dBmV)
- Channel count
- T3 timeouts

Profile:

- Download profile (Mbit/s)
- Upload profile (Mbit/s)

Binary sensors:

- Cable issue
- Internet outage
- Upstream timeouts present
- Internet access

Switches and buttons:

- Pause integration
- Verbose diagnostics
- Release session
- Restart modem

### Diagnostics

For troubleshooting or a GitHub issue, download a diagnostic file from:

**Settings > Devices & services > Ziggo Modem > three-dot menu > Download diagnostics**

The download is also available from the modem device page. It contains the
integration settings, coordinator status, endpoint results and the latest modem
API data. Passwords, usernames, tokens, local IP addresses, serial numbers, MAC
addresses and network identifiers are automatically redacted. Review the file
before sharing it publicly.

### Problem history

Connection interruptions and completely failed updates are stored persistently,
so the counters survive Home Assistant restarts. An interruption is counted
only when the modem changes from reachable to unreachable. A failed update is
counted when all modem API endpoints fail; an isolated endpoint failure remains
visible in API diagnostics but does not increase this counter. The last modem
restart is estimated from the uptime reported by the modem.

### Notes

- Uses an undocumented Ziggo modem API.
- Works locally only.
- OFDM values may differ per firmware version.
- Primarily tested on Sagemcom Ziggo modems.

---

## Nederlands

Lokale Home Assistant integratie voor Ziggo kabelmodems (Sagemcom).

Deze integratie geeft inzicht in je DOCSIS-verbinding, zoals signaalkwaliteit,
stabiliteit, fouttellers en netwerkstatus. De integratie werkt lokaal en gebruikt
geen SmartWifi Web of externe Ziggo-website.

### Functies

- Modemstatus en uptime
- Modemmodel, firmware, hardware, serienummer en MAC-adres in apparaatinfo
- Downloadbare Home Assistant-diagnostiek met privacyfilter
- Instelbare DOCSIS-signaalgrenzen
- Blijvende geschiedenis van onderbrekingen en mislukte updates
- Downstream signaalanalyse (power, SNR, fouten)
- Upstream monitoring (power, timeouts)
- SC-QAM en OFDM foutanalyse
- Detectie van download- en uploadprofiel
- Timestamp van laatste succesvolle update
- API-status per endpoint
- Optionele uitgebreide diagnostiek met kanaaldetails

### Installatie

#### HACS (aanbevolen)

1. Ga naar **HACS > Integraties**.
2. Klik op **drie puntjes > Custom repositories**.
3. Voeg deze repository toe.
4. Kies categorie **Integration**.
5. Installeer **Ziggo Modem**.
6. Herstart Home Assistant.

#### Handmatig

1. Kopieer `custom_components/ziggo_modem` naar je Home Assistant
   configuratiemap.
2. Herstart Home Assistant.

### Configuratie

De integratie werkt via de Home Assistant UI:

**Instellingen > Apparaten & diensten > Integratie toevoegen > Ziggo Modem**

Voer in:

- IP-adres (standaard: `192.168.100.1`)
- Gebruikersnaam (optioneel; laat leeg voor modems met alleen een wachtwoord)
- Wachtwoord
- Taal: `Nederlands` of `English`

De integratie vereist directe lokale toegang tot de modeminterface/API. Het
lokale modem-IP moet bereikbaar zijn vanaf Home Assistant. SmartWifi Web of
cloud-login wordt niet gebruikt.

### Opties

Open **Instellingen > Apparaten & diensten > Ziggo Modem > Configureren** om de
volgende grenzen aan te passen:

- Minimale downstream power (standaard: `-10 dBmV`)
- Maximale downstream power (standaard: `10 dBmV`)
- Minimale downstream SNR (standaard: `34 dB`)
- Maximale upstream power (standaard: `52 dBmV`)

Deze grenzen worden gebruikt voor de signaalkwaliteit, storingsclassificatie en
de kabelprobleemsensor. De standaardwaarden behouden het oorspronkelijke gedrag
van de integratie. De kabelprobleemsensor gebruikt een extra veiligheidsmarge
om niet op kleine schommelingen te reageren.

### Sensoren

Algemeen:

- Modemstatus
- Uptime
- Signaalkwaliteit
- Signaalkwaliteit uitleg
- Signaalkwaliteit advies
- Lijnstabiliteit
- API-status
- Laatste succesvolle update
- Verbindingsonderbrekingen
- Mislukte updates
- Laatste modemherstart
- Storingsclassificatie

Downstream:

- Downstream power (dBmV)
- Downstream SNR (dB)
- Aantal kanalen
- Gelockte kanalen
- SC-QAM / OFDM fouten

Upstream:

- Upstream power (dBmV)
- Aantal kanalen
- T3 timeouts

Profiel:

- Downloadprofiel (Mbit/s)
- Uploadprofiel (Mbit/s)

Binary sensors:

- Kabelprobleem
- Internet storing
- Upstream timeouts aanwezig
- Internettoegang

Switches en buttons:

- Integratie pauzeren
- Uitgebreide diagnostiek
- Sessie vrijgeven
- Modem herstarten

### Diagnostiek

Download voor probleemonderzoek of een GitHub-issue een diagnostiekbestand via:

**Instellingen > Apparaten & diensten > Ziggo Modem > menu met drie punten >
Diagnostiek downloaden**

De download is ook beschikbaar op de apparaatpagina van het modem. Het bestand
bevat de integratie-instellingen, coordinatorstatus, endpointresultaten en de
laatste modem-API-data. Wachtwoorden, gebruikersnamen, tokens, lokale
IP-adressen, serienummers, MAC-adressen en netwerkidentificatie worden
automatisch afgeschermd. Controleer het bestand voordat je het openbaar deelt.

### Probleemgeschiedenis

Verbindingsonderbrekingen en volledig mislukte updates worden blijvend
opgeslagen, zodat de tellers een herstart van Home Assistant overleven. Een
onderbreking telt alleen wanneer het modem van bereikbaar naar onbereikbaar
gaat. Een mislukte update telt wanneer alle modem-API-endpoints falen; een fout
van een los endpoint blijft zichtbaar in de API-diagnostiek maar verhoogt deze
teller niet. De laatste modemherstart wordt geschat via de uptime die het modem
rapporteert.

### Opmerkingen

- Gebruikt een ongedocumenteerde Ziggo modem API.
- Werkt alleen lokaal.
- OFDM-waarden kunnen verschillen per firmware.
- Primair getest op Sagemcom Ziggo modems.

---

## Disclaimer

This project is not affiliated with Ziggo.

Dit project is niet gelieerd aan Ziggo.

Use at your own risk. API endpoints may change with firmware updates.

Gebruik op eigen risico. API endpoints kunnen wijzigen bij firmware-updates.

---

## Contributing / Bijdragen

See [CONTRIBUTING.md](CONTRIBUTING.md).

Zie [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License / Licentie

This project is licensed under the **MPL-2.0 license**.

Dit project valt onder de **MPL-2.0 licentie**.
