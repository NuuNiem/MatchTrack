
# MatchTrack

Sovellus, jolla voi seurata käymiään jalkapallo-otteluita.

## Toiminnot

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen. *valmis*
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan otteluita, joita on käynyt katsomassa. *valmis*
- Käyttäjä pystyy valitsemaan ottelulle yhden tai useamman kategorian (Liiga, Cupin ottelu, Harjoituspeli, Ystävyysottelu). *valmis*
- Käyttäjä näkee sovellukseen lisäämänsä ottelut listana. *valmis*
- Käyttäjä pystyy etsimään otteluita otsikon tai kuvauksen perusteella. *valmis*
- Käyttäjä pystyy kommentoimaan toisten käyttäjien otteluita. *valmis*
- Sovelluksessa on käyttäjäsivu, joka näyttää tilastoja (lisättyjen otteluiden ja kommenttien määrä). *valmis*
- Sovellus tallentaa tiedot tietokantaan ja näyttää ne käyttäjäkohtaisesti. *valmis*

## Sovelluksen asennus

Asenna Flask:

```bash
pip install Flask
```

Alusta tietokanta:

```bash
python3 app.py init-db
```

Jos päivität olemassa olevan tietokannan, aja myös migraatio:

```bash
python3 migrate_add_custom_category.py
```

Lisää testidataa halutessasi:

```bash
python3 app.py seed-db
```

Tämä luo 20 käyttäjää, 60 ottelua ja 50 kommenttia. Kaikilla käyttäjillä on salasana: `testpass123`

Käynnistä sovellus:

```bash
flask run
```

## Suuren datamäärän testaus

Sovellus on testattu 1200+ ottelulla:

```bash
python3 test_large_data.py
```

**Testitulokset:**
- Tietokannassa 1261 ottelua
- Sivutus: 20 ottelua per sivu = 64 sivua
- COUNT-kysely: 0.19ms
- Sivutettu kysely (sivu 1): 1.08ms
- Hakukysely (HJK): 0.18ms
- Sivutettu kysely (sivu 26): 2.46ms

**Johtopäätökset:**
- ✅ Kaikki kyselyt suoritetaan alle 50ms:ssa
- ✅ Indeksit `match.title` ja `match.description` sarakkeissa optimoivat haut
- ✅ Sivutus estää kaikkien otteluiden lataamisen kerralla
- ✅ Sovellus toimii hyvin 1200+ ottelulla

