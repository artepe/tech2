# Saab: CIM, TWICE, ECU, avaimet ja osanumeroiden yhteensopivuus

Tämä on **turvallinen diagnostiikka- ja korjaussuunnitelma**, ei lukituksen tai ajoneston ohitusopas. Yksityiskohtaiset valmistajan sallimat korjaustoimenpiteet tarkistetaan **oikean auton VIN:iin, vuosimalliin ja WIS/TIS-versioon** perustuvasta huolto-ohjeesta.

## 1. Erota Saabin arkkitehtuurit

| Ajoneuvoperhe | Järjestelmä | Huomio |
| --- | --- | --- |
| Saab 9-3 (9400), 1998–2002 | TWICE-keskeinen avain-/ajonestojärjestelmä | Valikkoihin kuuluu TWICE; älä käytä CIM-ohjeita sellaisenaan. |
| Saab 9-3 Sport (9440), noin 2003–2012 | CIM (Column Integration Module) ja ECM:n välinen avain-/turvatietojen suhde | CIM sisältää myös ohjauspyörän kulma-anturitoimintoja. |
| Saab 9-5 (9600) | Mallivuoden mukaan eri moduulit ja moottorinohjaimet | WIS:n SPS- ja turvaohjeet tarkastetaan erikseen. |

WIS:n mukaan Saab 9-3 (9440) -avainkoodit liittyvät CIM:iin, ECM:ään ja avaimiin. On olemassa 'transport mode' -tilassa oleva uusi ohjainlaite ja aiemmin autoon liitetty, myöhemmin poistettu laite. Nämä **eivät ole sama lähtötilanne**.

### Dokumentoitu kapasiteetti (9-3 9440)

Saab WIS:n 2010 kuvauksen mukaan 9440-mallin CIM:ssä on **enintään viisi aktivoitua yksilöllistä avainkoodipaikkaa**. Uuden CIM:n *master key code* voi kyseisen kuvauksen mukaan muuttua ensimmäisen hyväksytyn Add-prosessin aikana; jo käytetyllä CIM:llä on erilaiset sidontaedellytykset. Tätä kapasiteettia ei voi suurentaa pelkällä OpenTech2-käyttöliittymän laskurimuutoksella, emmekä oleta sille toimivaa ohitusta. Eri Saab-sukupolvien rajoitukset voivat poiketa toisistaan. [WIS-lähde](https://saabwisonline.com/9-3-9440/2010/3-electrical-system/theft-protection/technical-description/key-code).

## 2. Tekniset tarkistukset ennen käytetyn CIM:n tai ECU:n hankintaa

Kirjaa *jokaisesta* osasta:
- Ajoneuvo: merkki, korimalli, mallivuosi, moottori, vaihteisto, markkina-alue ja alkuperäinen VIN.
- Yksikkö: fyysinen osanumero, muutossarja, laitteistoversio, ohjelmistoversio ja kalibrointitunniste.
- Sähköinen sopivuus: liittimet, pinout, virran ja maadoituksen kytkentä, väylä ja ohjainlaitteen sukupolvi.
- Toiminnallinen sopivuus: erilliset varusteet, anturit, airbag/ESP-variantti, immobilizer/avainten sijainti ja ajoneuvon konfiguraatio.
- Valmistajan vahvistama korvaava osa / supersessio: **vain vahvistettu** vastaavuus on hyväksyttävä yhteensopivuusväite.
- Lähtötila: uusi/transport mode, aiemmin yhdistetty käytetty osa tai valmistajan menetelmällä irrotettu osa.

**Eri osanumero ei automaattisesti tarkoita väärää osaa, mutta myöskään samankaltainen liitin tai sama osanumero ei yksin todista ohjelmointikelpoisuutta.** Supersessio on vahvistettava valmistajan osaluettelosta.

## 3. Turvapääsy: valmistajan sallittu työnkulku

- Määritä omistajuus tai kirjallinen valtuutus ajoneuvon huoltoon.
- Tarkista, mitä autentikointia **oikea** mallivuosi vaatii: TIS2000, GlobalTIS, TIS2Web tai muu valmistajan tukema huoltopalvelu.
- Huollossa tarkistetaan VIN ja ajoneuvon tiedot valmistajan dokumentaation mukaisesti.
- Ennen mitään moduulin vaihtoa dokumentoi kaikki nykyiset tunnisteet ja vikakoodit.
- Varmista oikea osa ja hyväksytty kalibrointi. Käytä virallista Add/Remove- ja SPS-menettelyä vain silloin, kun WIS niin määrää.
- Huollon jälkeen tarkista vikakoodit ja järjestelmien toiminta. Ohjauskulmaanturi voi edellyttää erillistä valmistajan kalibrointia.

**Avainten maksimimäärät tai CIM-/ECU-sidonnat eivät ole yleisiä käyttöliittymän laskureita.** Ne voivat olla riippuvaisia ECU:n muistirakenteesta, turvallisuusarkkitehtuurista ja sertifioidusta ohjelmistosta. Niiden pakotettu ohittaminen voi tehdä auton käynnistyksestä ja turvallisuusjärjestelmistä epäluotettavia.

## 4. Virallinen moduulinvaihto vs. kielletty oletus

| Tilanne | Oikea lähtökohta |
| --- | --- |
| ECM:n ohjelmisto on vanha | Tarkista SPS/TIS:n hyväksytty päivitys VIN:n ja ECU:n mukaan. |
| CIM tai ECM on viallinen | Tarkista valmistajan hyväksymä korvaava osanumero ja vaihdon jälkitoimet. |
| Käytetty CIM on toisesta autosta | Selvitä laitteen huoltohistoria ja virallinen kelpoisuus; älä arvaa, että siirto onnistuu. |
| Avaimia lisätään huollossa | Käytä valmistajan ohjeen mukaista varmentamista; huomioi nykyisten avainten läsnäolo ja järjestelmäkohtainen kapasiteetti. |
| Osa ei täsmää osanumerolistaan | Etsi dokumentoitu supersessio; älä kierrä ohjelmiston yhteensopivuustarkistuksia. |
| Kaikki avaimet puuttuvat | Tarkista omistajuuteen perustuva OEM/valtuutetun lukkosepän palautusmenetelmä. |

Avaimien oppimisen, seed-key-vastausten, immobilizer/VIN-sidonnan purkamisen tai väärennetyn osanumeroidentiteetin toteutusta ei sisällytetä projektiin.

## 5. Ohjelmointia edeltävä muistilista

1. Ajoneuvon oikea VIN ja henkilön huoltovaltuutus varmistettu.
2. Huolto-ohje ja valmistajan tukema diagnostiikkaohjelmisto valittu.
3. Oikea moduulityyppi, osanumero/supersessio ja kalibrointi varmistettu.
4. Ajoneuvon viat ja ohjainlaitteiden nykyiset tunnisteet dokumentoitu.
5. Vakaa jännitehuolto valmistajan vaatimusten mukaan; muut virrankuluttajat pois.
6. Kokoonpanon, varianttien ja turvajärjestelmän jälkitoimet selvitetty.
7. Suoritus tapahtuu valmistajan ohjelmistolla ja luvallisella käyttöoikeudella; OpenTech2 Bridge ei lähetä ohjelmointikomentoja.

## Lähteet

- [SAAB WIS: 9-3 (9440) avainkoodi, CIM ja ECM](https://saabwisonline.com/9-3-9440/2010/3-electrical-system/theft-protection/technical-description/key-code)
- [SAAB WIS: Security Access / TIS2000](https://saabwisonline.com/9-3-9440/2011/0-general/tech-2/technical-description/get-security-access)
- [SAAB WIS: CIM:n sähköiset ja toiminnalliset ominaisuudet](https://saabwisonline.com/9-3-9440/2003/2-engine/4-cylinder-petrol/engine-management-system-trionic-t8/technical-description/column-integration-module-703)
- [SAAB WIS: 9-3 (9400) TWICE-valikko](https://saabwisonline.com/9-3-9400/2002/3-electrical-system/twice/fault-diagnosis-general/tech-2-menu-structure)
- [SAAB WIS: 9-5 SPS, virransyöttö, keskeytysriski](https://saabwisonline.com/9-5-9600/2003/0-general/tis-2000/technical-description/service-programming)
