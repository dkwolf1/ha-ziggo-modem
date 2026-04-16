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

## 🔧 Ziggo Modem - Home Assistant Integration

Local Home Assistant integration for Ziggo (Sagemcom) cable modems.

This integration provides detailed insight into your DOCSIS connection, including signal quality, channel statistics, error rates and connectivity health — all locally, without cloud dependencies.

---

## ✨ Features

- Modem status & uptime
- Downstream signal analysis (power, SNR, errors)
- Upstream signal monitoring (power, timeouts)
- SC-QAM vs OFDM error separation
- Speed profile detection (download / upload)
- Cable quality classification (Goed / Matig / Slecht)
- Binary sensors for connection issues
- Fully local API (no cloud)

---

## 📦 Installation

### HACS (Recommended)

1. Go to **HACS → Integrations**
2. Click **⋮ → Custom repositories**
3. Add this repository  
4. Select **Integration**
5. Install **Ziggo Modem**
6. Restart Home Assistant

---

### Manual

1. Copy: custom_components/ziggo_modem into your Home Assistant config directory

2. Restart Home Assistant

---

## ⚙️ Configuration

The integration is fully UI-based:

**Settings → Devices & Services → Add Integration → Ziggo Modem**

Enter:
- IP address (default: `192.168.100.1`)
- Username
- Password

---

## 📊 Sensors

### General
- Modem Status
- Uptime
- Internet Toegang
- Kabelkwaliteit

### Downstream
- Downstream Power (dBmV)
- Downstream SNR (dB)
- Channel count
- Locked channels
- Errors (SC-QAM / OFDM)

### Upstream
- Upstream Power (dBmV)
- Channel count
- T3 timeouts

### Speed Profile
- Download Profiel (Mbit/s)
- Upload Profiel (Mbit/s)

---

## 🚨 Binary Sensors

- Kabelprobleem
- Internet Toegang Verloren
- Upstream Timeouts Aanwezig

---

## ⚠️ Notes

- Uses undocumented Ziggo modem API
- Works only locally (192.168.100.1)
- OFDM metrics may vary per modem firmware
- Designed for Sagemcom-based Ziggo modems

---

## ⚖️ Disclaimer

This project is not affiliated with Ziggo.

Use at your own risk. API endpoints may change with firmware updates.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 License

This project is licensed under the **MPL-2.0 License**
