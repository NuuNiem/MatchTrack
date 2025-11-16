
# MatchTrack

Sovellus, jolla voi seurata käymiään jalkapallo-otteluita.

## Toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen. *valmis*
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan otteluita, joita on käynyt katsomassa. *valmis*
- Käyttäjä pystyy lisäämään ottelulle tietoja, kuten päivämäärän, vastustajan, tuloksen, sijainnin ja mahdollisia muistiinpanoja ottelusta. *kesken*
- Käyttäjä näkee sovellukseen lisäämänsä ottelut listana. *valmis*
- Käyttäjä pystyy etsimään ja suodattamaan otteluita vastustajan, päivämäärän tai sijainnin perusteella. *valmis*
- Sovelluksessa on käyttäjäsivu, joka näyttää tilastoja, kuten katsottujen otteluiden lukumäärän, suosituimmat joukkueet ja käyntimäärän eri stadioneilla. *ei toteutettu*
- Käyttäjä pystyy tarkastelemaan tilastoja myös graafisessa muodossa. *ei toteutettu*
- Sovellus tallentaa tiedot tietokantaan ja näyttää ne käyttäjäkohtaisesti. *valmis*

## Sovelluksen asennus

Aktivoi virtuaaliympäristö:

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Asenna flask-kirjasto:

```bash
pip install Flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```bash
flask run
```

