# Redirect Builder

Nástroj na automatické generovanie presmerovaní pri migrácii WordPress webu.  
Zadáte dve adresy – dostanete hotové súbory pripravené na import.

---

## Na čo slúži

Pri presune webu na novú štruktúru URL sa staré adresy stanú nefunkčnými. Bez presmerovaní strácate pozície v Google a návštevníci narážajú na chybu 404.

Tento nástroj automaticky:

- zistí všetky staré URL vášho webu z histórie Wayback Machine a sitemáp
- porovná ich s URL nového webu
- vygeneruje hotové súbory pre import do WordPressu

---

## Dve verzie

| Verzia | Súbor | Čo potrebujete |
|---|---|---|
| Základná | `redirect_builder.py` | len Python a internet |
| Pro | `redirect_builder_pro.py` | Python + dva bezplatné API kľúče |

**Základná verzia** zbiera URL automaticky. Mapovanie starých adries na nové vyplníte ručne v tabuľke (alebo s pomocou AI).

**Pro verzia** navyše stiahne aktuálne indexované stránky cez Tavily a automaticky navrhne mapovanie pomocou Gemini. Vy len skontrolujete neisté riadky.

---

## Požiadavky

- Python 3.8 alebo novší – [python.org](https://python.org)
- Knižnica `requests`:

```bash
pip install requests
```

---

## Rýchly štart – základná verzia

```bash
python redirect_builder.py https://stary-web.sk https://novy-web.sk
```

Skript vygeneruje `redirects_PRACOVNY.csv`. Otvorte ho v Exceli alebo Google Sheets, doplňte stĺpec `destination` a spustite konvertor:

```bash
python redirect_builder.py --konvert https://novy-web.sk
```

---

## Rýchly štart – pro verzia

Najskôr nastavte API kľúče (postup nižšie), potom:

```bash
python redirect_builder_pro.py https://stary-web.sk https://novy-web.sk
```

Gemini automaticky navrhne mapovanie. Skontrolujete riadky označené `[?]` a `[??]`, prípadne opravíte a spustíte konvertor:

```bash
python redirect_builder_pro.py --konvert https://novy-web.sk
```

---

## Ako nástroj zbiera URL

Zdroje sa kombinujú – ak jeden zlyhá, ostatné pokračujú.

```
robots.txt  ->  sitemap XML          (automatická detekcia, vždy)
Wayback Machine CDX API              (história webu, zadarmo, vždy)
Tavily Search API                    (aktuálne Google indexované URL, len pro verzia)
```

Ručné zálohy pre prípad, že automatika nestačí:

- `google_site.txt` – URL z Google (základná verzia, postup nižšie)
- `novy_web_urls.txt` – URL nového webu, ak nemá sitemap

---

## Výstupné súbory

Po spustení `--konvert` dostanete tri súbory naraz. Použite jeden podľa toho, ako spravujete WordPress.

| Súbor | Použitie |
|---|---|
| `redirects_redirection_plugin.csv` | Plugin [Redirection](https://wordpress.org/plugins/redirection/) – zadarmo, odporúčame |
| `redirects.htaccess` | Priamy zápis do Apache, bez pluginu |
| `redirects_rankmath_pro.csv` | Rank Math Pro – Redirections → Import |

### Import cez plugin Redirection

1. Nainštalujte plugin: WP Admin → Pluginy → Pridať nový → hľadajte **Redirection**
2. Po aktivácii: WP Admin → Nástroje → Redirection → Import/Export
3. Zvoľte **Import from CSV**
4. Nahrajte `redirects_redirection_plugin.csv`

### Import do Rank Math Pro

1. WP Admin → Rank Math → Redirections
2. Kliknite **Import**
3. Nahrajte `redirects_rankmath_pro.csv`

---

## API kľúče – pro verzia

Oba kľúče sú bezplatné.

### Tavily

1. Zaregistrujte sa na [tavily.com](https://tavily.com)
2. Otvorte [app.tavily.com/account/api-keys](https://app.tavily.com/account/api-keys)
3. Skopírujte kľúč – začína `tvr_`

Free tier: 1 000 kreditov mesačne. Na jednorazovú migráciu webu postačí.

### Gemini

1. Otvorte [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Kliknite **Create API key**
3. Skopírujte kľúč – začína `AIza`

Model Gemini 2.0 Flash je zadarmo bez obmedzení využitia.

---

## Nastavenie API kľúčov

### Možnosť A – premenné prostredia (odporúčame)

**Mac / Linux:**
```bash
export TAVILY_API_KEY=tvr_xxxxxxxxxxxx
export GEMINI_API_KEY=AIzaXXXXXXXXXXXX
```

**Windows (cmd):**
```
set TAVILY_API_KEY=tvr_xxxxxxxxxxxx
set GEMINI_API_KEY=AIzaXXXXXXXXXXXX
```

Kľúče platia pre aktuálne okno terminálu. Pri novom otvorení ich zadajte znova.

### Možnosť B – priamo v súbore

Otvorte `redirect_builder_pro.py` a na začiatku doplňte:

```python
TAVILY_API_KEY = "tvr_xxxxxxxxxxxx"
GEMINI_API_KEY = "AIzaXXXXXXXXXXXX"
```

---

## Interpretácia AI mapovania – pro verzia

Gemini ku každému riadku pridá hodnotenie istoty do stĺpca `note`.

| Označenie | Význam | Odporúčaný postup |
|---|---|---|
| `[OK]` | Jasná zhoda | Môžete nechať bez kontroly |
| `[?]` | Pravdepodobná zhoda | Odporúčame skontrolovať |
| `[??]` | Nízka istota | Vyžaduje manuálnu opravu |

---

## Ručný fallback – google_site.txt

Ak chcete doplniť URL, ktoré Wayback Machine neobsahuje:

1. Do Googlu zadajte `site:stary-web.sk`
2. Nainštalujte rozšírenie [Instant Data Scraper](https://chrome.google.com/webstore/detail/instant-data-scraper/) (Chrome, zadarmo)
3. Spustite scraper na stránke s výsledkami
4. Exportujte URL do súboru `google_site.txt` (jeden riadok = jedna URL)
5. Spustite skript znova

---

## Po spustení nového webu

Odporúčame aktivovať monitor chýb 404, aby ste zachytili adresy, ktoré ste pri migrácii prehliadli.

**Rank Math (bezplatná verzia):**  
WP Admin → Rank Math → Všeobecné nastavenia → 404 Monitor → Zapnúť

Po týždni prevádzky skontrolujte log a doplňte chýbajúce presmerovania.

---

## Časté otázky

**Wayback Machine beží veľmi dlho.**  
Je to normálne pri weboch s väčším množstvom obsahu. Čakajte, nevypínajte terminál.

**Sitemap sa nenašla.**  
Skript pokračuje ďalej a upozorní vás. Vytvorte súbor `novy_web_urls.txt` s URL nového webu (jeden riadok = jedna URL) a spustite skript znova.

**Gemini navrhol zlé mapovanie.**  
Skontrolujte riadky označené `[?]` a `[??]` a opravte ich ručne v CSV pred spustením `--konvert`.

**Chcem len Rank Math Pro formát.**  
Všetky tri výstupné súbory sa generujú vždy naraz. Použite `redirects_rankmath_pro.csv`.

---

## Poznámky

- Skript nezapisuje nič na server. Všetky súbory zostávajú lokálne.
- Pri veľkom počte URL (1 000+) môže Wayback Machine trvať 2–3 minúty.
- Pre produkčné nasadenie odporúčame pred importom zálohovať databázu WordPressu.
