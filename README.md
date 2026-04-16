# Ziggo Modem - Home Assistant Integration

Local Home Assistant integration for Ziggo cable modems (Sagemcom).

## Features

- Modem status & uptime
- Downstream / upstream signal analysis
- Error monitoring (SC-QAM / OFDM)
- Speed profile detection (download / upload)
- Cable quality assessment
- Binary sensors for issues and connectivity

## Installation

### HACS (recommended)

1. Add this repository as a custom repository
2. Select "Integration"
3. Install "Ziggo Modem"
4. Restart Home Assistant

### Manual

1. Copy `custom_components/ziggo_modem` into your HA config
2. Restart Home Assistant

## Configuration

Use the UI:

Settings → Devices & Services → Add Integration → Ziggo Modem

## Sensors

### General
- Modem Status
- Uptime
- Internet Toegang
- Kabelkwaliteit

### Downstream
- Power
- SNR
- Errors (SC-QAM / OFDM)
- Channel count

### Upstream
- Power
- Timeouts

### Profile
- Download Profiel
- Upload Profiel

## Binary Sensors

- Kabelprobleem
- Internet Toegang Verloren
- Upstream Timeouts

## Notes

- Uses undocumented local modem API
- Works only in local network (192.168.100.1)
- OFDM values may be vendor-specific

## Disclaimer

This project is not affiliated with Ziggo.

## Contributing

See CONTRIBUTING.md

## License

MPL-2.0
