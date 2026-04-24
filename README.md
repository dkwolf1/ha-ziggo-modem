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

## 🔧 Ziggo Modem - Home Assistant Integratie

Lokale Home Assistant integratie voor Ziggo kabelmodems (Sagemcom).

Deze integratie geeft diepgaand inzicht in je DOCSIS-verbinding, zoals signaalkwaliteit, stabiliteit, fouttellingen en netwerkstatus — volledig lokaal en zonder cloud.

---

## ✨ Features

- Modemstatus en uptime
- Downstream signaalanalyse (power, SNR, fouten)
- Upstream monitoring (power, timeouts)
- SC-QAM en OFDM foutanalyse
- Snelheidsprofiel detectie (download / upload)

### 📊 Geavanceerde diagnostiek

- **Signaalkwaliteit**
  - Goed / Matig / Slecht
  - Inclusief score, reden, uitleg en advies

- **Lijnstabiliteit**
  - Stabiel / Licht wisselend / Instabiel
  - Gebaseerd op gedrag over tijd (errors + timeouts)

- **Kabelprobleem detectie**
  - Alleen bij echte DOCSIS-problemen
  - Geen false positives na reboot
  - Gebaseerd op rate (per uur) i.p.v. absolute waarden

- **API Status**
  - OK / Tijdelijke fouten / Instabiel / Gepauzeerd
  - Geeft inzicht in integratie en modem communicatie

- Volledig lokale API (geen cloud afhankelijkheid)

---

## 📦 Installatie

### HACS (aanbevolen)

1. Ga naar **HACS → Integraties**
2. Klik op **⋮ → Custom repositories**
3. Voeg deze repository toe
4. Kies categorie **Integration**
5. Installeer **Ziggo Modem**
6. Herstart Home Assistant

---

### Handmatig

1. Kopieer: custom_components/ziggo_modem naar je Home Assistant configuratiemap

2. Herstart Home Assistant

---

## ⚙️ Configuratie

De integratie werkt volledig via de UI:

**Instellingen → Apparaten & Diensten → Integratie toevoegen → Ziggo Modem**

Voer in:
- IP-adres (standaard: `192.168.100.1`)
- Gebruikersnaam
- Wachtwoord

---

## 📊 Sensoren

### Algemeen
- Modemstatus
- Uptime
- Signaalkwaliteit
- Signaalkwaliteit uitleg
- Signaalkwaliteit advies
- Lijnstabiliteit
- API status

### Downstream
- Downstream Power (dBmV)
- Downstream SNR (dB)
- Aantal kanalen
- Gelockte kanalen
- Fouten (SC-QAM / OFDM)

### Upstream
- Upstream Power (dBmV)
- Aantal kanalen
- T3 timeouts

### Snelheidsprofiel
- Downloadprofiel (Mbit/s)
- Uploadprofiel (Mbit/s)

---

## 🚨 Binary sensors

- Kabelprobleem
- Internet storing
- Upstream timeouts aanwezig
- Internettoegang

---

## ℹ️ Uitleg sensoren

- **Internettoegang**
  → geeft aan of het modem verbinding heeft met het netwerk

- **Signaalkwaliteit**
  → technische beoordeling van DOCSIS waarden (SNR, power, errors)

- **Lijnstabiliteit**
  → geeft aan hoe stabiel de verbinding zich gedraagt over tijd

- **Kabelprobleem**
  → alleen actief bij duidelijke technische problemen (niet bij kleine afwijkingen)

- **API status**
  → status van de integratie en communicatie met het modem

---

## ⚠️ Opmerkingen

- Gebruikt een ongedocumenteerde Ziggo modem API
- Werkt alleen lokaal (192.168.100.1)
- OFDM-waarden kunnen verschillen per firmware
- Primair getest op Sagemcom Ziggo modems

---

## ⚖️ Disclaimer

Dit project is niet gelieerd aan Ziggo.

Gebruik op eigen risico. API endpoints kunnen wijzigen bij firmware-updates.

---

## 🤝 Bijdragen

Zie [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 Licentie

Dit project valt onder de **MPL-2.0 licentie**
