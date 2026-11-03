# ECU-lukudiagnostiikka v0.2 — CAN/ISO-TP ja ajoneuvon VIN

Tämä laajennus toteuttaa **oikean, rajatun UDS 0x22 ReadDataByIdentifier -kyselyn** Linuxin kernelin ISO-TP-socketin kautta sekä geneerisen OBD-II Mode 09 PID 02 -VIN-luvun ELM327-adapterista. Mukana ovat demot ja automaattiset testit. Ei uutta ECU-koodausta eikä Saab Tech 2 -korttiemulaatiota.

## Mitä voit kokeilla heti MacBookilla

```bash
cd tech2
git pull
source .venv/bin/activate
python -m pip install -e '.[dev,serial]'
python -m pytest -q
opentech2 ecu-read --demo
opentech2 serve --demo
```

Avaa http://127.0.0.1:8765 ja valitse **ECU-tunnisteet**.

- **Lue VIN adapterista** näyttää demossa testitunnisteen; kun käynnistät ilman `--demo` ja yhdistät USB ELM327:n, se pyytää oikean auton VIN:n Mode 09 PID 02 -palvelulla, jos tuettu.
- **Näytä testivastaukset** tuottaa simuloidut UDS-vastaukset VIN:lle (F190), osanumerolle (F187) ja ohjelmistonumerolle (F188).
- **Lue oikea ECU** käyttää ainoastaan Linuxin SocketCAN + kernel ISO-TP -yhteyttä. Macissa tämän napin pitäisi ilmoittaa, ettei kuljetus ole käytettävissä.

## UDS-standardin rajatut DID:t

| DID | Käyttö |
| --- | --- |
| F190 | VIN |
| F187 | Valmistajan varaosanumero |
| F188 | ECU-ohjelmistonumero |
| F189 | ECU-ohjelmistoversio |
| F18C | ECU-sarjanumero |
| F191 | ECU-laitteistonumero |
| F192 | ECU-toimittajan laitteistonumero |
| F195 | ECU-toimittajan ohjelmistoversio |

Osoitteiden ja tietojen **tuki on ECU-kohtaista**. Negatiivinen vastaus, esimerkiksi `7F 22 31`, on ilmoitus siitä, ettei pyyntöä tueta; ohjelma näyttää sen 'ei saatavilla' -tilana. Ei diagnostiikkasession vaihtoa, tietoturva-avauksia tai yrittämistä toisilla koodeilla.

## Linux: CAN_ISOTP-kuljetuksen valmistelu

**Älä kytke tuntemattomia pinnejä autoon**. Tarvitset luotettavan SocketCAN-yhteensopivan CAN-liitännän ja hyväksytyn ajoneuvokohtaisen pinout-/väyläohjeen.

1. Tarkista Linuxissa, että CAN_ISOTP-kernelmoduuli on saatavilla:

```bash
sudo modprobe can-isotp
python3 -c 'import socket; print(hasattr(socket, "CAN_ISOTP"))'
```

2. Testaa ensiksi virtuaalisella, **autosta irrallisella** CAN-liitännällä:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
opentech2 ecu-read --demo
```

Pelkkä `vcan0`-liitäntä ei sisällä simuloitua ECU-vastaajaa. Todellinen `ecu-read --interface vcan0` aikakatkaistaan, ellei samassa virtuaaliväylässä ole erikseen toteutettua ISO-TP-vastaajaa.

3. Vasta kun ajoneuvon dokumentaatio on varmistanut käytetyn CAN-liittimen, nopeuden ja **fyysisen** ECU:n TX/RX-diagnostiikkatunnisteet, voit yrittää lukuyhteyttä:

```bash
# HUOM: 0x7E0 / 0x7E8 ovat yleisiä esimerkkitunnisteita,
# eivät Saab CIM/ECM -osoitteiden vahvistus.
opentech2 ecu-read --interface can0 --tx-id 0x7E0 --rx-id 0x7E8 --dids F190,F187,F188
```

Fyysinen yhteys **ei ole testattu oikealla autolla**. Toimintaa ei voi taata edes oikeilla TX/RX-osoitteilla, jos ECU ei käytä UDS 0x22:ta.

## Miksi Saab 9-3 (9440) on erikoistapaus

Saab WIS:n mukaan P-bus käyttää 500 kbit/s ja I-bus 33 kbit/s; CIM yhdistää näitä väyliä ja niiden välinen liityntä on valmistajakohtainen. **Älä syötä tavallisen kaksijohtimisen CAN-adapterin johdinta I-väylään vain nopeuden perusteella.** Saabin Tech 2 / CANdi ei ole sama asia kuin geneerinen UDS/SocketCAN. TWICE-sukupolvi 9-3 (9400) ei myöskään ole sama kuin 9440 CIM.

Käytännössä v0.2 on **perustyökalu mahdollisesti UDS-yhteensopivien ECU:iden identiteetin lukemiseen**, ei vielä Saab CIM:n tai TWICE:n valmistajaprotokollan toteutus. Vaikka ohjelma lukisi ECU:n VIN:n, se ei todista kaikkien ohjainlaitteiden näkyvän eikä niiden keskinäisen sidonnan toimivuutta.

## Turvallisuus- ja testirajaus

- Käyttöliittymä toimii `127.0.0.1`-osoitteessa, API-POST vaatii istuntotunnisteen.
- Palvelu `0x22` ja koodissa nimenomaisesti sallitut DID:t; ei raakakomentojen syöttöä.
- Enintään kuusi DID-pyyntöä yhtä kertalukua kohti; ei osoiteskannausta.
- `0x7DF`-funktionaalinen broadcast torjutaan CAN-pyynnöissä.
- Kysy ECU:n tunnisteet vain laitteesta, jonka diagnostiikkaan sinulla on lupa.
- Ei `0x27` SecurityAccess, `0x2E` WriteDataByIdentifier, `0x34` RequestDownload, avainten ohjelmointia tai ajoneston ohitusta.
- VIN näkyy ohjelmassa kysyttäessä, mutta sitä ei tallenneta tiedostoon tai lähetetä pilveen.

## Lähteet

- [Saab WIS 9-3 (9440) 2011: P-bus, I-bus, CIM gateway](https://saabwisonline.com/9-3-9440/2011/3-electrical-system/bus-and-diagnostics-communication/technical-description/detailed-description)
- [Saab WIS: Tech 2 + CANdi, 9-3 (9440)](https://saabwisonline.com/9-3-9440/2008/3-electrical-system/bus-and-diagnostics-communication/fault-diagnosis-general/diagnostic-concept)
- [python-can-isotp: Linux kernel SocketCAN ISO-TP documentation](https://can-isotp.readthedocs.io/en/latest/isotp/socket.html)
- [ISO 14229 DID identifier list, py-uds reference](https://uds.readthedocs.io/en/latest/pages/knowledge_base/did.html)
