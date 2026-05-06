# Navod pre pouzivatela

Tento navod predpoklada, ze mas nainstalovany Python 3.8 alebo novsi.  
Ak nie, stiahni ho na [python.org](https://python.org).

---

## Ktoru verziu pouzit?

**Zakladna verzia (`redirect_builder.py`)**  
Nepotrebujes ziadne API kluce. URL zo stareho webu zbieras automaticky cez Wayback Machine a sitemapu. Mapovanie source -> destination vyplnas rucne (alebo s pomocou Claude / ChatGPT).

**Pro verzia (`redirect_builder_pro.py`)**  
Potrebujes dva bezplatne API kluce (Tavily a Gemini). Skript sam navrhne mapovanie. Ty len skontroluj nejiste riadky a spusti konvertor.

---

## Zakladna verzia – krok po kroku

### 1. Inštalacia

Otvor terminal (na Windows: Win + R, napis `cmd`, stlac Enter).

```
pip install requests
```

### 2. Prvé spustenie

```
python redirect_builder.py https://stary-web.sk https://novy-web.sk
```

Ak oba weby su na rovnakej domene (len sa zmenila struktura URL):

```
python redirect_builder.py https://web.sk
```

Skript sa opytal na novy web – mozes zadat Enter (pouzije tu istu domenu).

### 3. Co sa stane

Skript:
- Najde sitemap automaticky cez robots.txt
- Stiahne historicke URL z Wayback Machine (moze trvat 1-3 minuty)
- Porovna stare a nove URL
- Vygeneruje `redirects_PRACOVNY.csv`

### 4. Vyplnanie CSV

Otvor `redirects_PRACOVNY.csv` v Exceli alebo Google Sheets.

Stlpce:
- `source` – stara URL (uz vyplnena)
- `destination` – nova URL (toto musíš doplnit)
- `type` – kod redirectu (301 je spravny, nemen)

Tip: Vlep obsah CSV do Claude alebo ChatGPT spolu so zoznamom URL noveho webu a popros o navrhnutie destination.

### 5. Konverzia

Po vyplneni uulož CSV a spusti:

```
python redirect_builder.py --konvert https://novy-web.sk
```

Vygeneruju sa tri subory:
- `redirects_redirection_plugin.csv`
- `redirects.htaccess`
- `redirects_rankmath_pro.csv`

### 6. Import do WordPressu

Odporucane: **Plugin Redirection** (zadarmo).

1. Nainštaluj plugin: WP Admin -> Pluginy -> Pridat novy -> hladaj "Redirection"
2. Po aktivacii: WP Admin -> Nastroje -> Redirection -> Import/Export
3. Zvol "Import from CSV"
4. Nahraj `redirects_redirection_plugin.csv`
5. Hotovo

---

## Pro verzia – krok po kroku

### 1. Ziskanie API klucov

**Tavily** (zbieranie URL z Google):
1. Registruj sa na [tavily.com](https://tavily.com)
2. Otvor [tavily.com/account/api-keys](https://app.tavily.com/account/api-keys)
3. Skopiruj kluc (zacina `tvr_`)

**Gemini** (AI mapovanie):
1. Otvor [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Klikni "Create API key"
3. Skopiruj kluc (zacina `AIza`)

### 2. Nastavenie klucov

**Mac / Linux** – zadaj do terminalu:

```
export TAVILY_API_KEY=tvoj_kluc_sem
export GEMINI_API_KEY=tvoj_kluc_sem
```

**Windows** – zadaj do cmd:

```
set TAVILY_API_KEY=tvoj_kluc_sem
set GEMINI_API_KEY=tvoj_kluc_sem
```

Poznamka: Kluce platia len pre toto okno terminalu. Pri novom spusteni terminalu ich treba zadat znova, alebo ich vloz priamo do skriptu (pozri README).

### 3. Spustenie

```
python redirect_builder_pro.py https://stary-web.sk https://novy-web.sk
```

Skript automaticky:
- Najde sitemap
- Stiahne URL z Wayback Machine
- Stiahne URL z Tavily (co Google aktualne indexuje)
- Porovna stare a nove URL
- Navrhne mapovanie cez Gemini
- Vygeneruje `redirects_PRACOVNY.csv` s vyplnenou destination

### 4. Kontrola CSV

Otvor `redirects_PRACOVNY.csv`. Stlpec `note` obsahuje:
- `[OK]` – Gemini si je isty. Skontrolovat nemusis, ale mozes.
- `[?]` – Gemini si nie je uplne isty. Odporuca sa skontrolovat.
- `[??]` – Gemini hádal. Urcite skontrolovat a opravit.

Riadky s prazdnou `destination` taktiez doplnit rucne.

### 5. Konverzia a import

Rovnaky postup ako zakladna verzia:

```
python redirect_builder_pro.py --konvert https://novy-web.sk
```

Potom importuj `redirects_redirection_plugin.csv` cez plugin Redirection.

---

## Casté problémy

**"pip nie je rozpoznany prikaz"**  
Skus `pip3 install requests` alebo `python -m pip install requests`.

**Wayback Machine trva dlho**  
Normalne pre weby s tisickami URL. Cakaj, nevypinaj.

**Sitemap nenajdena**  
Skript to povie a pokracuje dalej. Vytvor `novy_web_urls.txt` (jeden riadok = jedna URL) a spusti znova.

**Gemini vracia chybne mapovania**  
Normalne pre URL s nejasnymi slovami. Skontroluj riadky `[?]` a `[??]` a oprav rucne.

**"Neplatny API kluc"**  
Skontroluj, ci si kluc skopiroval celý a ci nema medzery na zaciatku alebo konci.

**Chcem len Rank Math Pro format**  
Vsetky tri formaty sa generuju vzdy naraz. Pouzij `redirects_rankmath_pro.csv`.

---

## Po spusteni noveho webu

1. Zapni 404 monitor: Rank Math -> General Settings -> 404 Monitor -> ON
2. Po tyzdni skontroluj 404 logy
3. Doplnaj missing redirecty podla 404 logu

---

## Podpora

Ak nieco nefunguje, otvor Issue na GitHube s:
- Verziou Pythonu (`python --version`)
- Chybovou hlaskou (skopiruj cely vystup z terminalu)
- Domenou (ak je verejne dostupna)
