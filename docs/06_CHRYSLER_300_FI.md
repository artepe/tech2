# Chrysler 300 / 300C / 300M — kaikki sukupolvet

**Tila:** automallien tiedot ja mallivuoden valinta on toteutettu OpenTech2:een. **Oikeiden Chrysler-ohjainlaitteiden OEM-diagnostiikkaa ei vielä ole toteutettu tai testattu.** OpenTech2 v0.2 on riippumaton projekti eikä alkuperäinen GM Tech 2/Chrysler wiTECH -testeri.

## Mallivuosikattavuus

| Vuosimallit | Profiili | Mahdollinen diagnostiikkaarkkitehtuuri | Tämän version toiminto |
| --- | --- | --- | --- |
| 1999–2004 | Chrysler 300M LH, mm. Special | Chrysler PCI/J1850-aikakauden järjestelmät; ei geneeristä CAN-oletusta | Geneerinen OBD-II ELM327-USB:llä, jos auto ja adapteri tukevat |
| 2005–2010 | Chrysler 300, 300C, 300C Touring/CRD Euroopassa, 300C SRT8 | CAN-C, diagnostic CAN-C, CAN-B ja LIN (varusteista riippuen) | Geneerinen OBD-II; OEM-moduulit eivät vielä toimi |
| 2011–2017 | 300, 300C, 300S, alueelliset SRT-versiot | CAN-C ja CAN-IHS; osa ECU:ista tarvitsee erillisen rajapinnan | Geneerinen OBD-II; OEM-moduulit eivät vielä toimi |
| 2018–2023 | 300, 300S, 300C, 2023 300C 6.4 HEMI | CAN-C, CAN-IHS, SGW-suojaus diagnostiikkatoimintoihin | Geneerinen OBD-II siltä osin kuin sallittu; ei SGW-avausta |

**Huom:** Vanhempaa, historiallista 1955–1965 *300 letter series* -sarjaa käsitellään erillisenä historiarekisterinä. Se ei tue sähköistä OBD-II-testeriä. Chrysler 300:n tuotanto päättyi vuonna 2023; vuoden 2024–2026 uusia Chrysler 300 -vuosimalleja ei ole.

Tämä on mallivuosittainen **profiilikatalogi**, ei todistettu täydellinen moottori- ja ECU-osanumeroluettelo. Markkina-alue, korimalli, moottori ja varusteet voivat muuttaa järjestelmiä. Yllä olevat aikakausiluokat eivät takaa tietyn auton sisäisen väylän tavoitettavuutta tavallisesta OBD-portista.

## Näin valitset oikean profiilin

Päivitä lähdekoodi:

```bash
cd ~/tech2
git pull
source .venv/bin/activate
python -m pip install -e '.[serial]'
opentech2 serve --demo
```

Avaa **http://127.0.0.1:8765**, siirry **Chrysler 300** -välilehdelle, anna vuosimalli ja paina **Näytä profiili**. Ohjelma näyttää profiilin, diagnostisten väylien tiedot sekä sen, mitä ohjelma **ei vielä tue**.

Kun saat USB ELM327 -adapterin ja oikean auton testiin:
1. Pysäytä demo `Ctrl+C` ja käynnistä `opentech2 serve` ilman `--demo`-valintaa.
2. Yhdistä vasta oikean auton OBD-liittimeen ja Macin USB-porttiin. Tarkista `ls /dev/cu.*`.
3. Käytä yleiskuvan automerkkinä Chrysler ja mallikentässä oikeaa mallia sekä vuotta. Vain geneerinen OBD-II -luku on toteutettu.
4. Kokeile moottorin mittausarvoja, päästöjärjestelmän DTC-lukua ja VIN:iä, jos auto tukee sitä.
5. Kirjaa mitkä toiminnot onnistuvat sekä adapterin ja auton tiedot GitHub Issuesiin **ilman auton koko VIN:iä tai henkilökohtaisia tunnistetietoja**.

**Älä** kokeile näennäisillä CIM-, SGW-, RF Hub-, WIN- tai ECU-komentoprofiileilla ECU-koodausta. Ohjelman profiilit eivät lähetä niitä, eikä SGW-suojauksen kiertämistä ole toteutettu. SGW-suojatuissa huoltotöissä käytetään valmistajan hyväksymää pääsyä. OBD-II-diagnostiikan read-only-toiminnot voivat olla mahdollisia myös SGW-laitteellisissa autoissa, mutta kyseinen yksilö täytyy testata.

## Varmennetut tekniset lähteet

- [Mopar: 300M 1999–2004](https://store.mopar.com/v-chrysler-300m)
- [Stellantis: Chrysler 300 -tuotannon päättyminen 2023](https://blog.stellantisnorthamerica.com/2023/12/09/last-legend-off-the-line-2023-chrysler-300c-ends-production/)
- [Chrysler 300 2005: CAN-C/CAN-B/LIN, huolto-opas](https://charm.li/Chrysler/2005/300%20V6-3.5L%20VIN%20G/Repair%20and%20Diagnosis/Powertrain%20Management/Computers%20and%20Control%20Systems/Information%20Bus/Description%20and%20Operation/)
- [FCA wiTECH Secure Gateway – hyväksytty pääsy](https://kb.fcawitech.com/print-903.html)
- [Appcar DiagFCA: 2011–2023 300/CAN-IHS-tukilista](https://appcar-diagfca.com/en/supported-vehicles/chrysler-300-lx/)

## Jatkokehitys

Vahvista ensin USB ELM327:llä toimivat geneeriset lukutoiminnot kaikissa sukupolvissa ja kerää luotettavat, henkilötiedoista puhdistetut testivektorit. Toteuta vasta sitten vuosimallikohtaiset, dokumentoidut ja luvalliset OEM-mittausarvo- ja vikakoodilukijat. Mahdolliset moduulien kirjoitus-/ohjelmointityönkulut vaativat erillisen ajoneuvokohtaisen soveltuvuuden, valtuutuksen ja turvallisuusarvion. 
