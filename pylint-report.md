# Pylint-raportti

Pylint antaa seuraavan raportin sovelluksesta:

```
************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:16:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:24:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:31:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:40:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module routes
routes.py:1:0: C0114: Missing module docstring (missing-module-docstring)
routes.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
routes.py:16:0: C0116: Missing function or method docstring (missing-function-docstring)
routes.py:21:0: C0116: Missing function or method docstring (missing-function-docstring)
routes.py:21:0: R0915: Too many statements (127/50) (too-many-statements)
************* Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)

------------------------------------------------------------------
Your code has been rated at 9.50/10
```

Käydään seuraavaksi läpi tarkemmin raportin sisältö ja perustellaan, miksi kyseisiä asioita ei ole korjattu sovelluksessa.

## Docstring-ilmoitukset

Suuri osa raportin ilmoituksista on seuraavan tyyppisiä ilmoituksia:

```
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:17:0: C0116: Missing function or method docstring (missing-function-docstring)
```

Nämä ilmoitukset tarkoittavat, että moduuleissa ja funktioissa ei ole docstring-kommentteja. Sovelluksen kehityksessä on tehty tietoisesti päätös, ettei käytetä docstring-kommentteja. Funktioiden nimet ovat riittävän kuvaavia ja sovelluksen rakenne on yksinkertainen, joten docstringit eivät tuo merkittävää lisäarvoa koodin ymmärrettävyyteen.

Esimerkiksi funktiot kuten `get_db()`, `close_db()`, `csrf_protect()`, `init_db()` ja `seed_db()` ovat niin selkeitä nimiltään, että niiden tarkoitus on helppo ymmärtää ilman erillistä dokumentaatiota. Samoin reittifunktiot noudattavat Flaskin standardikäytäntöjä, jolloin niiden toiminta on itsestään selvää Flask-sovelluksen kontekstissa.

## Liian monta lausetta

Raportissa on seuraava ilmoitus liittyen funktioiden lausemäärään:

```
routes.py:21:0: R0915: Too many statements (106/50) (too-many-statements)
```

Tämä ilmoitus koskee `init_routes()`-funktiota, joka sisältää 106 lausetta, kun Pylint suosittelee maksimissaan 50 lausetta. Funktio sisältää kaikki sovelluksen reitit ja niiden käsittelijät.

Tämän rakenteen hajottaminen vaatisi sovelluksen arkkitehtuurin uudelleenjärjestelyä, esimerkiksi Flaskin blueprinttien käyttöönottoa. Pienen sovelluksen kohdalla (noin 10 reittiä) tämä olisi tarpeettoman monimutkaista. Nykyinen rakenne pitää kaikki reitit yhdessä paikassa, mikä tekee sovelluksen kokonaisuuden ymmärtämisestä helppoa. Kaikkien endpointien näkeminen yhdellä silmäyksellä on hyödyllistä pienen sovelluksen kohdalla.
