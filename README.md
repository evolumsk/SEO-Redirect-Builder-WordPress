# Redirect Builder

Automaticke generovanie redirect mapy pri migrácii WordPress webu.  
Vstup: dve URL. Vystup: hotove subory pre Redirection plugin, .htaccess a Rank Math Pro.

---

## Verzie

| Subor | Zavislosti | Automatizacia |
|---|---|---|
| `redirect_builder.py` | len `requests` | zbieranie URL, manualné mapovanie |
| `redirect_builder_pro.py` | `requests` + Tavily API + Gemini API | zbieranie URL + AI mapovanie |

---

## Rychly start – zakladna verzia

```bash
pip install requests
python redirect_builder.py https://stary-web.sk https://novy-web.sk
```

Skript vygeneruje `redirects_PRACOVNY.csv`. V nom dopln stlpec `destination`, potom:

```bash
python redirect_builder.py --konvert https://novy-web.sk
```

---

## Rychly start – pro verzia (s API)

```bash
pip install requests
export TAVILY_API_KEY=tvoj_kluc    # Mac/Linux
export GEMINI_API_KEY=tvoj_kluc    # Mac/Linux

# Windows:
# set TAVILY_API_KEY=tvoj_kluc
# set GEMINI_API_KEY=tvoj_kluc

python redirect_builder_pro.py https://stary-web.sk https://novy-web.sk
```

Pro verzia automaticky navrhne mapovanie cez Gemini. Skontroluj riadky `[?]` a `[??]`, potom:

```bash
python redirect_builder_pro.py --konvert https://novy-web.sk
```

---

## Zdroje URL

### Zakladna verzia

```
robots.txt -> sitemap   (automaticka detekcia, bez API)
Wayback Machine CDX     (historicke URL, zadarmo, bez API)
google_site.txt         (manuálny fallback – Instant Data Scraper)
novy_web_urls.txt       (manualny fallback pre novy web)
```

### Pro verzia

```
robots.txt -> sitemap   (automaticka detekcia)
Wayback Machine CDX     (historicke URL, zadarmo)
Tavily Search API       (aktualne Google indexovane URL)
novy_web_urls.txt       (manualny fallback pre novy web)
```

---

## Fallback retazec

Skript funguje aj bez sitemáp a bez API. Zdroje sa kombinujú – ak jeden zlyhá, ostatné pokračujú.

```
robots.txt -> sitemap
    |
    v
Wayback Machine CDX API
    |
    v  (len pro verzia)
Tavily Search API
    |
    v  (ak nič nefunguje)
manuálny google_site.txt / novy_web_urls.txt
```

---

## Vystupy

Vsetky tri formaty su generovane naraz po spusteni `--konvert`.

| Subor | Pouzitie |
|---|---|
| `redirects_redirection_plugin.csv` | Plugin [Redirection](https://wordpress.org/plugins/redirection/) – zadarmo, odporucane |
| `redirects.htaccess` | Priamy Apache, bez pluginu |
| `redirects_rankmath_pro.csv` | Rank Math Pro – Redirections -> Import |

---

## API kluce – kde ziskat

**Tavily** (pro verzia)  
[tavily.com/account/api-keys](https://tavily.com/account/api-keys)  
Free tier: 1000 kreditov / mesiac. Pre jednorazovu migraciu viac nez dosta.

**Gemini** (pro verzia)  
[aistudio.google.com/apikey](https://aistudio.google.com/apikey)  
Gemini 2.0 Flash: zadarmo.

---

## Nastavenie API klucov

### Moznost A – premenne prostredia (odporucane)

```bash
# Mac / Linux
export TAVILY_API_KEY=tvr_xxxxxxxxxxxx
export GEMINI_API_KEY=AIzaXXXXXXXXXXXX

# Windows
set TAVILY_API_KEY=tvr_xxxxxxxxxxxx
set GEMINI_API_KEY=AIzaXXXXXXXXXXXX
```

### Moznost B – priamo v subore

Otvor `redirect_builder_pro.py` a nastav na zaciatku:

```python
TAVILY_API_KEY = "tvr_xxxxxxxxxxxx"
GEMINI_API_KEY = "AIzaXXXXXXXXXXXX"
```

---

## Interpretacia AI mapovania (pro verzia)

| Oznacenie | Vyznam |
|---|---|
| `[OK]` | Vysoka istota – zhoda je jasna |
| `[?]` | Stredna istota – odporuca sa skontrolovat |
| `[??]` | Nizka istota – vyzaduje manualnu kontrolu |

Stlpec `note` v CSV obsahuje tieto oznacenia. Po kontrole a oprave spusti `--konvert`.

---

## Manualné fallbacky

### google_site.txt (zakladna verzia)

Ak chces doplnit URL z Google:
1. Do Google zadaj `site:stary-web.sk`
2. Nainštaluj [Instant Data Scraper](https://chrome.google.com/webstore/detail/instant-data-scraper/) (Chrome)
3. Exportuj URL do `google_site.txt` (jeden riadok = jedna URL)
4. Spusti skript znova

### novy_web_urls.txt

Ak novy web nema sitemap:
1. Vytvor subor `novy_web_urls.txt`
2. Vloz URL noveho webu (jeden riadok = jedna URL)
3. Spusti skript znova

---

## Inštalacia zavislosti

```bash
# Zakladna verzia
pip install requests

# Pro verzia
pip install requests
# google-generativeai sa nepouziva – Gemini sa vola cez HTTP priamo
```

---

## Poznamky

- Skript nezapisuje ziadne subory na server. Vsetky vystupy su lokalne.
- Odporucany import: Redirection plugin (zadarmo, spravuje redirecty cez WP Admin).
- Po spusteni noveho webu zapni 404 monitor: Rank Math (free) -> General Settings -> 404 Monitor -> ON.
- Ak mas tisicky URL, Wayback Machine moze trvat aj 2-3 minuty. Normalne.
