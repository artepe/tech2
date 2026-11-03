# Tech 2 -tutkimus- ja käyttömuistio (FI)

Tarkistettu 2026-11-03. Avoimen lähdekoodin **muistiinpanoja**, ei valmistajan oma ohjelmisto tai korvaava OEM-huolto-ohje. Tutkimuksessa erotetaan toisistaan dokumentoitu tuki, yleisesti kuvattu toiminto ja täysin toteuttamaton prototyyppi.

## 1. Mikä Tech 2 on

Tech 2 on GM/Vetronixin/Boschin aikakauden kädessä pidettävä huoltotesteri. Varsinainen Tech 2 sisältää näytön, näppäimistön, VCI-ajoneuvoyhteysmoduulin, sarjaliikenneportit ja ohjelmiston PCMCIA-muistikortilla. Kaikkia ajoneuvoja ja valmistajien kaikkia versioita ei voi diagnosoida yhdellä kortilla.

- **PCMCIA**: merkkikohtainen ohjelmistokanta. Valmistajan oppaassa varoitetaan käyttämästä väärän jännitetason korttia (5 V vs. 3,3 V). Kortti kuuluu ohjeistetulle paikalle, tyypillisesti Slot 1 / ylempi paikka.
- **VCI ja ajoneuvokaapeli**: diagnostinen yhteys auton DLC/OBD-pistokkeeseen. Liittimen muoto ei yksin takaa protokollayhteensopivuutta.
- **CANdi**: CAN Diagnostic Interface, tarvitaan niissä Tech 2:n tukemissa autoissa, jotka käyttävät tätä CAN-yhteyttä. Ei muuta ELM327-lukijaa Tech 2:ksi.
- **RS-232**: alkuperäisen Tech 2:n yhteys PC/TIS-työasemaan. Se ei tarkoita, että meidän Python-sovelluksemme voisi vielä ohjata Tech 2:ta.
- **TIS2000 / TIS2Web**: mallista ja aikakaudesta riippuvat valmistajan palveluohjelmat. Lisenssi-/pääsyvaatimukset voivat vaihdella.
- **SPS**: huolto-ohjelmoinnin polku ECU:n hyväksytyille kalibroinneille. Ei yleinen 'flash mikä tahansa tiedosto mihin tahansa ECU:un' -toiminto.

## 2. Ohjelmisto- ja ajoneuvoperheet

Historiallisesti Tech 2 -korttiperheitä: GM/Chevrolet/Cadillac/Buick, Saab, Opel/Vauxhall, Isuzu, Suzuki, Holden ja joitain GM:n alueellisia automerkkejä. Tuen **tarkka vuosimalli** riippuu kortin versiosta, markkina-alueesta, ECU:sta ja protokollasta. Ei pidä päätellä koko valmistajan kattavuutta.

GM/Australian julkaistu esimerkki: 1997–2009 suurelta osin Tech2/Tech2Win, vuosina 2010–2013 mallikohtainen siirtymä GDS2:een, vuosimallissa 2014 ja uudemmissa GM-ajoneuvoissa Australia/Uusi-Seelanti -lähteen mukaan GDS2. Älä sovella listaa automaattisesti kaikkiin maihin.

## 3. Tyypilliset alkuperäisen Tech 2:n valikot

Seuraava on **yleinen navigointikuvaus**; tarkat valinnat muuttuvat kortin, mallivuoden ja ECU:n mukaan.

| Valikko | Käyttötarkoitus | Saatavuus |
| --- | --- | --- |
| Diagnostics / F0 | Mallivuoden, automallin ja järjestelmän valinta | Autokohtainen |
| Diagnostic Trouble Codes | Vikakoodien ja niiden tilan lukeminen | Autokohtainen |
| Read Values | ECU:n reaaliaikaiset mittausarvot | Autokohtainen |
| Snapshot | Jäädytetty tai tallennettu diagnostiikkanäyte | Kortti-/järjestelmäkohtainen |
| System Information | ECU:n ohjelmisto-, laitteisto- tai tunnistetiedot | Järjestelmäkohtainen |
| Activate / Adjustment | Huoltotestit ja säädöt | Voi muuttaa fyysisiä toimilaitteita |
| Add/Remove | Joidenkin Saab-moduulien valmistajan ohjeistettu irtikytkentä/liittäminen | Vaatii mallikohtaiset edellytykset |
| SPS / Service Programming | Ohjainlaitteen tuettu huolto-ohjelmointi TIS:n kanssa | Erillinen valmistajan työnkulku |
| Tool Options / CANdi Diagnostics | Testerilaitteen oma diagnostiikka, CANdi POST | Laitteistokohtainen |

Toiminto ei ole saatavilla vain siksi, että vastaava otsikko näkyy toisessa Tech 2 -ohjelmistokortissa.

## 4. Alkuperäisen Tech 2:n turvallinen lukukäyttö

1. Tarkista ajoneuvon vuosimalli ja valmistajan huolto-ohje; valitse oikea ohjelmistokortti ja tarvittaessa CANdi.
2. Tarkista kaapeli, kortti ja akkujännite. Älä aseta väärän jännitteen PCMCIA-korttia.
3. Kytke DLC autoon, käynnistä Tech 2, valitse Diagnostics → oikea mallivuosi → oikea malli → ECU/järjestelmä.
4. Avaa **System Information** ja tallenna VIN, ECU:n tunnisteet, ohjelmistotunniste ja DTC:t silloin kun työkalu näyttää ne. Älä muuta niiden arvoja.
5. Avaa **Read Values** ja tallenna oireeseen liittyvät mittaukset. Älä suorita Activate/Adjustment-toimintoja ilman huolto-ohjeen turvamenettelyä.
6. Vertaa arvot WIS/GMSi/valmistajan huolto-ohjeiden odotusarvoihin. Kirjaa alkuperäiset tiedot ennen huoltotoimintoa.

## 5. SPS:n ymmärtäminen — ei yleisohitusta

TIS2000:n historiallinen **Request Information → PC/TIS-tarkistus → Program ECU** -työnkulku perustuu oikeaan VIN:iin, malliin, ohjainlaitteeseen ja valmistajan kalibrointiin. Eräissä Saab-malleissa Tech 2 siirtää ohjelmointitietoja auton ja PC:n välillä. Nykyisillä autoilla tuki, ohjelma ja käyttöoikeus voivat olla eri.

Ohjainlaitteen uudelleenohjelmointi voi tehdä ECU:sta käyttökelvottoman, jos jännite katkeaa. Tämän prototyypin käyttöliittymässä ei ole eikä tule automaattista 'ohita tarkistus ja ohjelmoi' -painiketta.

## 6. Jos Tech 2 ei saa yhteyttä

- Varmista oikea mallivuosi, korttiperhe ja tarvittaessa CANdi.
- Tarkista DLC:n virransyöttö, maadoitus, laitteiston sulakkeet ja adapteri.
- Tarkista että oikea virta-avaimen tila on käytössä (ECU-kohtaiset ohjeet).
- Osa autoista tarvitsee erikoisadapterin tai muut protokollat.
- Varmista PCMCIA:n kosketus; älä irrota tai vaihda korttia kesken ohjelmoinnin.
- CANdi-ohjelmiston tulee vastata Tech 2:n kortin versiota; katso valmistajan päivitysohje.

## 7. Ensisijaiset lähteet

1. [GM Tech2 User Guide, 2014, laite ja CANdi/SPS](https://gsitlc.ext.gm.com/userguides/GM_Tech2_User_Guide.pdf)
2. [Vetronix Tech 2 User Guide, 2006 (arkistokopio)](https://tech2wiki.com/content/media_archive/pdf/vetronix_tech2_users_guide.pdf)
3. [SAAB WIS: Get Security Access (9440 / 2011)](https://saabwisonline.com/9-3-9440/2011/0-general/tech-2/technical-description/get-security-access)
4. [SAAB WIS: Key Code (9440 / 2010)](https://saabwisonline.com/9-3-9440/2010/3-electrical-system/theft-protection/technical-description/key-code)
5. [SAAB WIS: SPS, Saab 9-5 / 2003](https://saabwisonline.com/9-5-9600/2003/0-general/tis-2000/technical-description/service-programming)
6. [SAAB WIS: Tech 2 menu structure (9400 / 2001)](https://saabwisonline.com/9-3-9400/2001/8-body/convertible/fault-diagnosis-general/tech-2-menu-structure)
7. [GM/Holden: diagnostiikkaohjelmiston valinta mallivuoden mukaan](https://www.holden.co.nz/content/dam/holden/oc/nz/en/index/complete-care/accident-care/02-pdf/gm-vehicles-supp-by-gds2-tech2-tech2win-2309.pdf)
8. [GM: yleistä GDS2 / Tech2 / Tech2Win diagnostiikasta](https://acdelcogmtrade.com.au/w/assets/documents/position-statements/GM%20Vehicles%20Supp%20by%20GDS2_Tech2_Tech2Win%20_2404.pdf)

PDF-lähteisiin viitataan linkkeinä, niiden tekijänoikeuksien alaista sisältöä ei kopioida tähän repoon.
