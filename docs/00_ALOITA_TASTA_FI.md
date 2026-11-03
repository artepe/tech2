# Aloita tästä — OpenTech2 Bridge v0.1

**Kaksi eri laitetta, kaksi eri toimintoa:**

- **GM/Vetronix Tech 2** on fyysinen huoltotesteri, jonka toiminnallisuus riippuu kortista, ajoneuvosta, CANdi-lisälaitteesta ja tarvittaessa valmistajan TIS/SPS-palvelusta.
- **OpenTech2 Bridge** tässä GitHub-repossa on riippumaton Python-ohjelma. Sen ajoneuvoyhteys tukee **vain geneeristä, lukevan tilan OBD-II-diagnostiikkaa ELM327-USB-adapterilla**. Se **ei ole Tech 2 -firmware**, se ei lue eikä aja PCMCIA-korttia, eikä siihen voi tällä hetkellä yhdistää alkuperäistä Tech 2 -testeriä.

## MacBook: 5 minuutin demokäynnistys

```bash
git clone https://github.com/artepe/tech2.git
cd tech2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[serial]'
opentech2 doctor
opentech2 serve --demo
```

Avaa selaimessa <http://127.0.0.1:8765>.

Demonäkymässä on:
1. **Yleiskuva**: valitse automerkki, malli ja vuosimalli omiin muistiinpanoihisi.
2. **Mittausarvot**: testiarvot esimerkiksi kierrosluvulle, ajonopeudelle ja moottorin lämpötilalle.
3. **Vikakoodit**: esimerkkikoodit P0420 ja P0130, **eivät oikean auton vikakoodeja**.
4. **Ohjelmistokortit**: tietokanta Tech 2 -korttiperheiden nimistä. Tämä **ei asenna kortin ohjelmistoa**.
5. **Turvapääsy**: listaa toiminnot, jotka **eivät ole käytettävissä** v0.1:ssä.

Lopeta painamalla Terminalissa Ctrl+C. Demo käynnistyy **ilman autoon yhdistämistä**.

## Oikean auton geneerinen OBD-II-luku

Tarvitset USB-sarjaportin kautta toimivan ELM327-yhteensopivan adapterin. Ajoneuvon ja adapterin yhteensopivuutta **ei ole vielä testattu** tässä projektissa. MacBookissa etsi portti:

```bash
ls /dev/cu.*
```

Kytke adapteri auton OBD-liittimeen, käytä autovalmistajan ohjeen mukaista virta-avaimen tilaa, käynnistä ohjelma ilman `--demo`-valintaa:

```bash
opentech2 serve
```

1. Avaa paikallinen osoite `http://127.0.0.1:8765`.
2. Valitse automerkki; tämä ei itsessään vaihda OEM-diagnostiikkaprotokollaa.
3. Syötä USB-portti, esimerkiksi `/dev/cu.usbserial-0001`.
4. Aloita oletusnopeudella 38400; adapterista riippuen vaihtoehtoina 9600, 57600 tai 115200.
5. Paina **Yhdistä**. Onnistumista ei voida luvata kaikille ELM327-klooneille.
6. Siirry **Mittausarvot** ja paina **Päivitä arvot**. Jos arvoa ei tueta, se näkyy puuttuvana.
7. Siirry **Vikakoodit** ja paina **Lue vikakoodit**. Nämä ovat geneerisiä OBD-II-päästöjärjestelmäkoodeja; ohjelma ei tällä hetkellä skannaa ABS-, SRS- tai korimoduuleja.
8. Katkaise yhteys käyttöliittymästä ennen adapterin irrotusta.

**Huom:** ohjelma ei lähetä virhekoodeja poistavia komentoja, ECU-ohjelmointia, seed-key-vastauksia eikä ajoneston/avainten komentoja.

## Korttitiedoston tunnistus ilman lataamista

Jos sinulla on oikeus hallita omaa alkuperäistä korttikuvaasi:

```bash
opentech2 cards add /polku/oma-tiedosto.bin --family saab --label "Oma Saab-kortti"
opentech2 cards list
```

Tämä laskee **vain SHA-256-tiivisteen ja tiedoston koon**. Se ei avaa ohjelmistokortin toimintoja, eikä tallenna itse kortin sisältöä rekisteriin.

## Testaus ja vianetsintä

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

- **Porttia ei löydy**: tarkista USB-sovitin ja sen ajuri; kokeile `ls /dev/cu.*` uudelleen.
- **Autoyhteyttä ei synny**: tarkista virran kytkentä, adapterin nopeus, OBD-tuki ja toimiva virtalähde. Viallinen kaapeli tai klooniadapteri on mahdollinen.
- **Tyhjä mittausarvo**: auto ei välttämättä tue kyseistä geneeristä PID:tä.
- **Tech 2 PCMCIA -kortti ei näy**: tarkoituksellista; Mac-ohjelma ei emuloi PCMCIA- tai Tech 2 -laitetta.
- **Avaimet/CIM/SPS ei toimi**: tarkoituksellista; ne eivät kuulu tähän lukevan tilan v0.1-sovellukseen.

Katso myös [Tech 2 -tutkimus](01_TECH2_TUTKIMUS_FI.md), [Saab / CIM / ECU](02_SAAB_CIM_ECU_FI.md) ja [suunnitelma](03_ARKKITEHTUURI_FI.md).
