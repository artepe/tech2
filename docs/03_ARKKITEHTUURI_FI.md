# OpenTech2 Bridge: arkkitehtuuri ja kehitysroadmap

## Nykyinen, oikeasti toteutettu (v0.1)

- Python + HTTP-serveri paikallisessa osoitteessa `127.0.0.1`.
- Auton valinta katalogista; katalogimerkintä **ei** tarkoita valmistajaprotokollan toteutusta.
- ELM327-tyyppinen USB-sarjaporttiadapteri: geneeriset OBD-II Mode 01 -arvot ja Mode 03 -vikakoodit. **Ei verifioitu oikealla autolla**.
- Offline-demo (erikseen merkitty). Sen arvot eivät perustu autoon.
- Seitsemän Tech 2 -korttiperheen luettelo ja *paikallisten* omien tiedostojen SHA-256-metatietorekisteri.
- Turvallisuusraja: ei ajoneuvon kirjoitustoimintoja, avain-/CIM-/ECU-koodausta eikä OEM-autentikoinnin ohitusta.

## Ehdotettu portaittainen suunnitelma

**Vaihe A — varmennettu lukudiagnostiikka**
- Oikeiden ELM327-/STN-adaptereiden integraatiotestit.
- Pyydettyjen OBD-II PID:ien tuen selvitys, ISO-TP-monikehysvastausten dekoodaus, DTC-tyyppien robusti käsittely.
- Lokitus/testit ja CSV-export ilman luottamuksellisia tunnisteita oletusarvoisesti.

**Vaihe B — avoimet kuljetuskerrokset**
- SocketCAN ja Linuxin ISO-TP autovalmistajan sallimille lukukomennoille.
- J2534-järjestelmäkirjastot ja erikseen tuetut CAN/K-line-adapterit.
- VCI-/CANdi-laitteiden tutkimus vain julkaistun dokumentaation, käyttäjän omien laitteiden ja asianmukaisen käyttöoikeuden puitteissa.
- Alkuperäinen Tech 2 → Mac Bridge -rajapinta **ei ole toteutettu eikä automaattinen**.

**Vaihe C — OEM-metatieto**
- Saab 9-3 (9400) TWICE, 9-3 (9440) CIM, 9-5 ECM; mallivuodet, valikot, anturiyksiköt, dokumentoidut huoltotehtävät.
- Opel/GM/Suzuki/Isuzu/Holden vain tarkastettujen dokumenttien ja testivektorien pohjalta.
- Moduuli- ja osanumeroinventaario, versiotiedot ja OEM:n vahvistamat supersessiot.
- Osanumeron kelpoisuusarvo **UNKNOWN** kun lähdettä ei ole; ei arvattua 'compatible'-statusta.

**Vaihe D — valtuutetut huoltotyönkulut**
- Erillinen valmistajan hyväksymä autentikointipalvelu ja käyttäjän todennus, jos dokumentoidusti tuettu ja luvallinen.
- Huolto-/SPS-toiminnot vasta, kun ajoneuvo-/mallikohtainen validaatio, tila-, virta-, kalibrointi-, valmistajan käyttöoikeus- ja palautusehdot on täytetty.
- Ei turvarajojen ohituskoodeja, rajattomien avainten väitteitä tai jokaisen ECU:n pakottavaa flashia.

## Offline-moduuli-inventaario

`opentech2 inventory examples/bench_modules.json` lukee JSON-tiedoston **ilman ajoneuvoyhteyttä**. Se sopii monen moduulin vertailuun. Siinä ei ole ohjelmallista rajoitusta rekisteröitävien moduulien tai avainten metatietomäärälle, mutta se **ei muuta auton oikeita laitteistorajoituksia**.

Ei VIN-/avain-/salaisuustietojen automaattista tallennusta.

Katso [aloitusohje](00_ALOITA_TASTA_FI.md), [Tech 2 -tutkimus](01_TECH2_TUTKIMUS_FI.md) ja [Saab-opas](02_SAAB_CIM_ECU_FI.md).
