# ELM327 USB — testausohje Saab-harrastajille (OpenTech2 v0.2)

**Tämä on varhainen avoimen lähdekoodin prototyyppi, ei alkuperäisen Tech 2 -testerilaitteen emulaattori.** Oikealla autolla ja adapterilla toimintaa ei ole vielä vahvistettu. Vain omalla tai huoltovaltuutetulla autolla; aloita paikallaan turvallisessa paikassa.

## 1 MacBook-asennus

Tarvitset Python 3.10:n tai uudemman ja Internet-yhteyden asennukseen.

```bash
python3 --version
# Uusi asennus:
git clone https://github.com/artepe/tech2.git
cd tech2

# Jos kloonasit jo aiemmin: käytä vain
# cd ~/tech2
# git pull

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[serial]'
opentech2 doctor
opentech2 serve --demo
```

Jos `python3 --version` näyttää **alle 3.10**, asenna uusi Python ensin (esimerkiksi [python.org](https://www.python.org/downloads/macos/)) ja varmista, että virtuaaliympäristö käyttää juuri sitä. Homebrew'lla on mahdollista asentaa `brew install python@3.12` ja luoda ympäristö käyttäen `"$(brew --prefix python@3.12)/bin/python3.12" -m venv .venv`.

`pip 21.2.4`, `File "setup.py" or "setup.cfg" not found` ja `opentech2: command not found` johtuvat yleensä siitä, että pakettia yritetään asentaa vanhalla Pythonilla/pipillä ilman toimivaa virtuaaliympäristöä. Suorita ensin `source .venv/bin/activate` ja tarkista `python --version` ja `python -m pip --version`.

### Avaa demo

Pääte näyttää onnistuessaan `OpenTech2 Bridge: http://127.0.0.1:8765`. **Jätä pääte auki.** Avaa Safarissa <http://127.0.0.1:8765>, tai uudessa Terminal-välilehdessä `open http://127.0.0.1:8765`.

Demo näyttää kuvitteellisia kierrosluku-, lämpötila- ja vikakooditietoja. Demo **ei ole yhteydessä autoon**. Lopeta `Ctrl+C`.

## 2 Tarvittava laitteisto

- Maciin liitettävä **USB-sarjaporttina näkyvä ELM327-yhteensopiva adapteri** ja ehjä OBD-II-liitäntä autossa.
- Bluetooth- ja Wi-Fi-ELM327-sovittimia sovellus ei tue suoraan tässä versiossa. USB-liitäntä ei yksin takaa laitteen ELM327-yhteensopivuutta.
- Saabissa geneerisen OBD-II:n saatavuus riippuu vuosimallista, moottorinohjauksesta ja markkina-alueesta. Tämä ei ole vielä Saab-spesifiä Tech 2 / CIM / TWICE -diagnostiikkaa.

## 3 Yhdistä oikeaan autoon

1. Pysäköi auto turvallisesti, kytke ELM327 OBD-liittimeen ja USB-kaapeli Maciin.
2. Avaa Macin Terminal, siirry `cd ~/tech2` ja aktivoi `source .venv/bin/activate`.
3. Etsi sarjaportti `ls /dev/cu.*`. Kirjaa adapterin kytkennän jälkeen ilmestynyt portti, esimerkiksi `/dev/cu.usbserial-0001`. Portin nimi vaihtelee adapterin mukaan.
4. Jos demo on jo käynnissä, lopeta se `Ctrl+C` ja käynnistä **ilman** `--demo`-valintaa:

```bash
opentech2 serve
```

5. Avaa <http://127.0.0.1:8765>, valitse merkiksi **Saab**, syötä oikea USB-sarjaportti ja valitse adapterin baudrate (kokeile ensin 38400).
6. Kytke autoon virta valmistajan huolto-ohjeen mukaisesti; käynnistyvän moottorin kanssa älä käsittele pyöriviä tai kuumia osia. Paina **Yhdistä**.
7. Kokeile **Mittausarvot → Päivitä arvot**, **Vikakoodit → Lue vikakoodit** ja **ECU-tunnisteet → Lue VIN adapterista**. Kaikki geneeriset PID:t eivät välttämättä ole autossa käytettävissä.
8. Merkitse muistiin, mitkä arvot toimivat. Katkaise yhteys ohjelmasta ennen USB-kaapelin irrottamista. **Älä testaa ajon aikana.**

**Autosta lähetetään vain geneerisiä OBD-II-lukupyyntöjä.** Ohjelma ei poista vikakoodeja, ohjelmoi avaimia, tee ECU-flashausta tai avaa CIM:n turvapääsyä.

## 4 Yleiset ongelmat

| Oire | Mahdollinen syy ja tarkistus |
| --- | --- |
| Safari ei yhdistä osoitteeseen 127.0.0.1:8765 | Palvelin ei ole käynnissä. Tarkista että Terminalissa lukee `OpenTech2 Bridge:` ja se on edelleen auki. |
| `No such file or directory: .venv/bin/activate` | Virtuaaliympäristö luomatta. Aja `python3 -m venv .venv` oikeassa `~/tech2`-kansiossa. |
| `setup.py or setup.cfg not found` | Vanha pip tai väärä ympäristö. Aktivoi .venv ja päivitä pip, setuptools ja wheel. |
| `opentech2: command not found` | Asennus keskeytyi tai .venv ei ole aktiivinen. Tarkista `which python` ja asenna paketti uudelleen. |
| Sarjaporttia ei näy | Tarkista USB-kaapeli ja sovittimen ajuri, käytä `ls /dev/cu.*`. Apple Silicon- ja Intel-Macit voivat tarvita eri ajurin; älä asenna tuntematonta ajuria. |
| Yhdistys epäonnistuu tai aikakatkaisu | Tarkista virtalukon tila, sarjaportin nimi, nopeus, OBD-tuki ja USB-kaapeli. |
| PID / VIN ei saatavilla | Auto ei ehkä tue sitä tai adapteri palauttaa odottamattoman vastauksen. V0.2:n parseri on vielä testauksessa. |
| CIM / TWICE / ABS / airbag puuttuu | Näihin ei ole tämän version valmistajakohtaista protokollatukea. |

## 5 Näin ilmoitat testituloksen

Tee GitHubiin testiraportti [Issues → New issue](https://github.com/artepe/tech2/issues/new/choose) valitsemalla **ELM327 test report** tai kerro nämä tiedot keskustelussa:

- Saab-malli, vuosimalli, moottori ja maa/markkina-alue
- Macin malli, macOS- ja Python-versio
- ELM327-USB-adapterin valmistaja/malli ja sarjaportin tyyppi (voit peittää sarjanumeron)
- Yhteys onnistui vai ei, toimivat mittausarvot, vikakoodien ja VIN-luvun tila
- Virheilmoitus tarkasti ja toistamisvaiheet
- Onko käytössä demo vai oikea auto

**Älä julkaise** auton koko VIN:iä, osoitetta, rekisteritunnusta, avaintietoja, turvakoodeja, tokenia, korttitiedostoja tai yksityisiä lokitietoja.

## Lisätiedot

- [Pääohje](00_ALOITA_TASTA_FI.md)
- [ECU ISO-TP / UDS](04_ECU_LUKUDIAGNOSTIIKKA_FI.md)
- [Projektin README](../README.md)

**Repo on julkinen:** Saab-harrastajat voivat lukea ohjeet ja lähettää testiraportin GitHub Issuesiin ilman erillistä kutsua.
