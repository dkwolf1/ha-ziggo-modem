# Ziggo Modem: metingen en storingen

[Wiki-startpagina](https://github.com/dkwolf1/ha-ziggo-modem/wiki/Home) | [English](https://github.com/dkwolf1/ha-ziggo-modem/wiki/English)

## Wat de integratie weet

Home Assistant logt via HTTPS in op de **lokale modem-API** en leest zes
endpoints: `state`, `downstream`, `primary_downstream`, `upstream`,
`serviceflows` en `softwareupdate`. De standaardinterval is 60 seconden
(instelbaar van 5 tot 3600 seconden). SmartWifi Web wordt niet gebruikt.

De integratie leest door het modem gerapporteerde DOCSIS-status, uptime,
kanaal-lock, power, SNR, fouttellers, timeouts, ingestelde serviceflow-snelheden
en `accessAllowed`. Model en firmware staan bij de apparaatinfo als het modem
die gegevens aanlevert. Een generieke modelnaam bewijst geen specifiek model.

De integratie **doet geen** ping naar websites, snelheidstest, meting van
latency of wifi-kwaliteit en navraag naar de storingsstatus van Ziggo. Ze kan
ook niet met zekerheid bepalen welke kabel, splitter, wandcontactdoos of
straatkast defect is. Een storingslabel is een *aanwijzing*, geen bewezen
oorzaak. Een goede score garandeert geen probleemloze internetervaring.

## Begin bij deze drie entiteiten

| Entiteit | Betekenis |
| --- | --- |
| **API Status** | Of het uitlezen van de lokale modem-API lukt. Bekijk `endpoint_status`, `failed_endpoints`, `consecutive_failures` en `last_successful_update`. Dit is niet de internetstatus. |
| **Signaalkwaliteit** | Berekende DOCSIS-score en label. De attributen `reden`, `score` en meetwaarden verklaren het label. |
| **Storingsclassificatie** | Een *mogelijke* oorzaak, gekozen volgens een prioriteitsvolgorde. Geen officiele Ziggo-storingsmelding. |

Deze entiteiten kunnen terecht verschillen. De API kan bereikbaar zijn
terwijl de DOCSIS-signalen slecht zijn. Andersom kan de lokale API falen
terwijl normaal internetgebruik nog werkt.

## DOCSIS-begrippen in gewone taal

- **Downstream** loopt van het kabelnet naar het modem; **upstream** loopt terug. Dit zijn richtingen van de kabelverbinding, geen gemeten download- of uploadsnelheid.
- **Power (dBmV)** is de door het modem gemelde signaalsterkte van een kanaal. Een waarde buiten de ingestelde grenzen is een aanwijzing, geen bewijs voor de plek van de fout.
- **SNR (dB)** vergelijkt signaal met ruis. De integratie gebruikt de laagste gemelde SC-QAM downstream SNR, waardoor een zwak kanaal de uitkomst kan beinvloeden.
- **Gelockt kanaal** betekent dat het modem meldt op dat DOCSIS-kanaal te zijn gesynchroniseerd. Ontbrekende lock kan de kabelverbinding beperken, maar de integratie kent de fysieke oorzaak niet.
- **Corrected/uncorrected errors** zijn modemtellers. Alleen uncorrected errors tellen mee in de kwaliteitsregels. Een opgelopen totaal is niet hetzelfde als een nieuwe foutpiek.
- **T3/T4-timeouts** zijn door het modem gemelde DOCSIS-timing-/ranginggebeurtenissen. Vergelijk ze met actuele verbinding en signaalwaarden; een oude tellerstand bewijst geen lopende storing.

## Signaalkwaliteit en Lijnstabiliteit

Signaalkwaliteit begint op **100 punten**. Onderstaande aftrekposten worden
opgeteld; het resultaat wordt minimaal nul. De standaardgrenzen zijn via
**Instellingen > Apparaten & diensten > Ziggo Modem > Configureren** aanpasbaar.

| Meting | Punten |
| --- | --- |
| Minstens een gerapporteerd downstreamkanaal niet gelockt | -35 |
| Gemiddelde SC-QAM downstream power buiten ingestelde onder-/bovengrens (standaard -10 tot +10 dBmV) | -25 |
| Gemiddelde SC-QAM downstream power dicht bij een grens (waarschuwingsmarge maximaal 2 dBmV) | -10 |
| Laagste SC-QAM downstream SNR onder ingestelde minimum (standaard 34 dB) | -40 |
| Laagste SC-QAM downstream SNR vanaf minimum tot onder minimum +3 dB | -25 |
| Laagste SC-QAM downstream SNR vanaf minimum +3 tot onder minimum +6 dB | -10 |
| Gemiddelde ATDMA upstream power boven ingestelde maximum (standaard 52 dBmV) | -35 |
| Gemiddelde ATDMA upstream power boven maximum -2 dBmV | -20 |
| Gemiddelde ATDMA upstream power boven maximum -4 dBmV | -10 |
| OFDM uncorrected errors per uptime-uur: >5000 / >1000 / >100 | -35 / -20 / -5 |
| SC-QAM uncorrected errors per uptime-uur: >100 / >10 | -15 / -5 |
| T3-timeouts per uptime-uur: >10 / >2 | -20 / -10 |

Bij een regel met meerdere gradaties telt **een** aftrekpost, niet alle
gradaties tegelijk. Score **80-100 = Goed**, **50-79 = Matig**, **0-49 =
Slecht**. De entiteiten Uitleg en Advies geven algemene tekst bij deze
score; het attribuut `reden` noemt de meetwaarden die meetelden. Een
ontbrekende kanaalwaarde levert geen aftrek op. Daarom bewijst een goede score
niet dat elk onderdeel daadwerkelijk gemeten is.

**Lijnstabiliteit** is Stabiel als de score minstens 80 is, de berekende
T3-frequentie nul is en de OFDM-frequentie onder 100 per uptime-uur blijft.
Bij een score van minstens 50 zonder deze combinatie is het Licht wisselend;
anders Instabiel. Dit zijn berekende labels, geen doorlopende metingen van
packet loss.

## Storingsclassificatie

Alleen de **eerste** passende categorie hieronder verschijnt. Andere
afwijkingen kunnen tegelijk aanwezig zijn: kijk ook naar Signaalkwaliteit en
Kabelprobleem.

| Label | Wanneer | Wat het wel en niet betekent |
| --- | --- | --- |
| Mogelijke provider-/CMTS-storing | Het modem meldt `accessAllowed` expliciet als onwaar | Het modem meldt geen toegang. Dit bewijst geen Ziggo-brede storing en identificeert geen CMTS. |
| Mogelijk kanaalprobleem | Minstens een gerapporteerd downstreamkanaal is niet gelockt | Er is een DOCSIS-kanaalprobleem zichtbaar. |
| Mogelijk coaxprobleem | Gemiddelde ATDMA upstream power > ingestelde maximum; of T3-frequentie >10 per uptime-uur; of gemiddelde SC-QAM downstream power buiten ingestelde grenzen; of SC-QAM-foutfrequentie >100 per uptime-uur | Deze waarden kunnen bij een coax-/RF-probleem passen; de fysieke plek is onbekend. |
| Mogelijke instraling / ruis | Laagste SC-QAM downstream SNR < ingestelde minimum; of OFDM-foutfrequentie >5000 per uptime-uur | Ruis of instraling is aannemelijk, niet bewezen. |
| Geen duidelijke storing | Geen van bovenstaande regels past | Geen passende regel, **niet** een garantie dat alles goed is. |

De precieze codevolgorde is: toegang geweigerd, kanaal niet gelockt, hoge
upstream power, hoge T3-frequentie, lage downstream SNR, hoge OFDM-frequentie,
downstream power buiten grens, hoge SC-QAM-frequentie, geen duidelijke
storing. Een hoge upstream power kan dus een tegelijk aanwezige lage SNR in
dit *ene* label overschaduwen.

## Binaire meldingen

| Entiteit | Wanneer aan |
| --- | --- |
| **Internettoegang** | De modemwaarde `accessAllowed` wordt als waar herkend. Dit is een melding van het modem, geen externe verbindingstest. |
| **Internet Storing** | `accessAllowed` wordt als onwaar herkend. Dit test niet zelf of websites bereikbaar zijn. |
| **Kabelprobleem** | Minstens een regel uit de tabel hieronder geldt. Bekijk `reason_codes`, `reasons` en de meetattributen. |
| **Upstream Timeouts Aanwezig** | Totaal gerapporteerde T4-timeouts >0, of T3-timeouts >5. Het zijn modemtellers, niet per se gebeurtenissen van dit uur. |

Ontbreekt `accessAllowed`, of is de waarde onbekend, dan staan zowel
Internettoegang als Internet Storing uit. Dat bewijst noch werkend internet,
noch een storing.

**Redencodes van Kabelprobleem:**

| `reason_codes` | Exacte regel |
| --- | --- |
| `downstream_channels_unlocked` | Minder gelockte dan totale downstreamkanalen. |
| `downstream_snr_low` | Laagste SC-QAM downstream SNR < ingestelde minimum min 1 dB. |
| `downstream_power_out_of_range` | Gemiddelde SC-QAM downstream power < ingestelde minimum min 2 dBmV, of > maximum plus 2 dBmV. |
| `upstream_power_high` | Gemiddelde ATDMA upstream power > ingestelde maximum. |
| `t4_timeouts_detected` | Totaal gerapporteerde T4-timeouts >0. |
| `ofdm_error_rate_high` | OFDM uncorrected errors / uptime-uren >5000. |
| `t3_timeout_rate_high` | T3-timeouts / uptime-uren >10. |

Kabelprobleem hanteert voor downstream SNR en power bewust een extra marge.
Daarom hoeft deze melding niet bij elke Matige of Slechte signaalscore aan te
gaan.

## Andere sensoren en grenzen van de meting

- **Downstream Power** is het gemiddelde van gerapporteerde SC-QAM-kanaalpower; **Downstream SNR** is de laagste SC-QAM-SNR. OFDM-kanalen tellen niet mee in deze twee samenvattingen. **Upstream Power** is het gemiddelde van ATDMA-kanalen.
- **Downstream Kanalen / Downstream Gelocked / Upstream Kanalen** tellen wat het modem meldt. Een ontbrekende kanaallijst kan als nul verschijnen.
- **DS Errors SC-QAM / DS Errors OFDM / Upstream T3 Timeouts** zijn sommen van modemtellers. Een totaal kan blijven staan tot de modemcounter wordt gereset; het hoeft geen nieuwe gebeurtenis te zijn.
- **OFDM Errors per uur / SC-QAM Errors per uur / T3 Timeouts per uur** delen cumulatieve tellers door de modem-uptime (minimale noemer een minuut). Het zijn *gemiddelden sinds de uptime begon*, niet over alleen het laatste uur.
- **OFDM Errors actueel per uur / SC-QAM Errors actueel per uur / T3 Timeouts actueel per uur** berekenen het verschil tussen succesvolle uitlezingen en schalen dat naar een uur. De eerste waarde is nul; als de teller daalt wordt de waarde weer nul. Deze sensoren staan standaard uit in het entiteitenregister. Bij een korte meetperiode kan een omgerekende uurwaarde groot lijken.
- **Downloadprofiel / Uploadprofiel** zijn de ingestelde `maxTrafficRate` van de eerste passende serviceflow, omgerekend naar Mbit/s. Dit is **geen** gemeten downloadsnelheid of uploadsnelheid.
- **Modem Status / Software Status** tonen ruwe statuswaarden van het modem. Hun precieze betekenis kan per firmware verschillen. Ook **Uptime** komt van het modem.
- **Laatste Modemherstart** is een schatting op basis van tijdstip nu minus de gemelde uptime; het modem levert deze datum niet rechtstreeks aan.

## API-fouten, beschikbaarheid en geschiedenis

**API Status** is `OK` zonder recente endpointfouten, `Tijdelijke fouten` bij
overbrugbare fouten, `Instabiel` na drie volledig mislukte updates achter
elkaar of als voor een fout endpoint geen bruikbare cachewaarde meer bestaat,
en `Gepauzeerd` wanneer het pollen bewust is stilgezet. Het attribuut
`endpoint_status` toont per endpoint `ok` of `failed` bij de laatste poging.
`primary_downstream` wordt wel uitgelezen maar heeft momenteel geen eigen
entiteit.

Bij een fout van een enkel endpoint houden afhankelijke entiteiten hun laatste
geslaagde waarde **minder dan 10 minuten** vast; andere endpoints kunnen
blijven verversen. Daarna worden die afhankelijke entiteiten onbeschikbaar.
Bij volledige API-uitval blijft de vorige coordinatordata ook minder dan
10 minuten zichtbaar; daarna worden entiteiten onbeschikbaar. API Status kan
bij langdurige volledige uitval zelf ook onbeschikbaar worden. Bekijk dan ook
de integratiestatus en Home Assistant-logs. `Gepauzeerd` betekent dat de
schakelaar Integratie pauzeren actief is, niet dat het modem uitgevallen is.
Een authenticatiefout start een herauthenticatieflow.

**Mislukte Updates** stijgt bij iedere volledig mislukte poll (alle endpoints
falen of authenticatie faalt). Een enkel falend endpoint telt niet mee.
**Verbindingsonderbrekingen** stijgt alleen als een eerder bereikbaar modem
volledig onbereikbaar wordt; een authenticatiefout is geen onderbreking. De
tellers blijven na een herstart van Home Assistant bestaan. **Laatste
succesvolle update** is de laatste poll waarbij minstens een endpoint werkte;
het betekent niet dat *alle* data toen vernieuwd is.

## Problemen oplossen

1. Controleer eerst **API Status**, `endpoint_status` en **Laatste succesvolle update**. Een falend endpoint wijst mogelijk op een API-/firmwareprobleem; bij alle endpoints kan ook lokale bereikbaarheid, login of modemuitval meespelen.
2. Test het lokale modem-IP vanaf het Home Assistant-netwerk, niet alleen vanaf een andere pc. Open `https://<modem-ip>` op hetzelfde netwerk. De integratie gebruikt `https://<modem-ip>/rest/v1`, geen externe Ziggo-website.
3. Bij **Ongeldige inloggegevens**: gebruik de herauthenticatiemelding en controleer het modemwachtwoord. Laat de gebruikersnaam leeg bij een modem met alleen een wachtwoord. Gebruik **Opnieuw configureren** als het IP-adres veranderde; verwijder de integratie niet.
4. Bij **Kan geen verbinding maken met modem**: controleer adres, routing, lokale modeminterface en API. **Onbekende fout** vraagt om onderzoek van de logs en is geen afzonderlijke kabelstoringscategorie.
5. Bij een kabel- of signaalwaarschuwing: vergelijk `reason_codes`, actuele waarden en ingestelde grenzen. Controleer toegankelijke coaxverbindingen en splitters. Blijft het signaal slecht of merk je uitval, neem dan met de meetwaarden contact op met Ziggo. Lees een oude tellerstand niet als een nieuwe storing.
6. Bij veel tijdelijke fouten: vergelijk pollinginterval, endpointstatussen en Home Assistant-logs. **Sessie Vrijgeven** wist het huidige inlogtoken van de integratie en vraagt een nieuwe uitlezing; het herstelt geen DOCSIS-signaal. **Modem Herstarten** vraagt echt om een modemherstart en onderbreekt de verbinding: gebruik dit bewust.

Download diagnostiek via **Instellingen > Apparaten & diensten > Ziggo Modem >
menu met drie punten > Diagnostiek downloaden**. Het bestand bevat instellingen,
endpointstatus en recente modemdata. Bekende geheimen en netwerkvelden worden
afgeschermd. **Controleer het bestand alsnog voordat je het openbaar deelt.**
Uitgebreide diagnostiek voegt kanaalattributen aan Signaalkwaliteit toe;
schakel het alleen tijdens onderzoek in.

## Meldingen bij het instellen

| Melding | Betekenis |
| --- | --- |
| **Ongeldige inloggegevens** | Het modem weigert de login of geeft geen bruikbaar token terug. |
| **Kan geen verbinding maken met modem** | Een login-/API-aanvraag faalt; controleer lokale bereikbaarheid en modeminterface. |
| **Onbekende fout** | Onverwachte instelfout; bekijk de Home Assistant-logs. |
| **Modem is al toegevoegd** | Een integratievermelding met hetzelfde modemadres bestaat al. |

Deze pagina beschrijft de huidige code, vooral getest op Sagemcom-modems
van Ziggo. Firmwareverschillen kunnen API-velden en OFDM-waarden veranderen.
