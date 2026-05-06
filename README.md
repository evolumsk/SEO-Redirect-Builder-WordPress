# Návod pre používateľa – základná (bezplatná) verzia

Tento návod popisuje základnú verziu nástroja `redirect_builder.py`, ktorá nevyžaduje žiadne API kľúče ani platené služby. Všetko funguje zadarmo – potrebujete len Python a pripojenie na internet.

---

## Obsah

1. [Čo nástroj robí](#čo-nástroj-robí)
2. [Požiadavky](#požiadavky)
3. [Inštalácia Pythonu](#inštalácia-pythonu)
4. [Nastavenie vo Visual Studio Code](#nastavenie-vo-visual-studio-code)
5. [Prvé spustenie skriptu](#prvé-spustenie-skriptu)
6. [Vyplnenie CSV súboru](#vyplnenie-csv-súboru)
7. [Konverzia do výstupných formátov](#konverzia-do-výstupných-formátov)
8. [Import do WordPressu – plugin Redirection](#import-do-wordpressu--plugin-redirection)
9. [Import do WordPressu – Rank Math Pro](#import-do-wordpressu--rank-math-pro)
10. [Overenie presmerovaní](#overenie-presmerovaní)
11. [Monitorovanie po spustení](#monitorovanie-po-spustení)
12. [Časté problémy a riešenia](#časté-problémy-a-riešenia)

---

## Čo nástroj robí

Keď presúvate web na novú štruktúru URL, staré adresy prestanú fungovať. Návštevníci narazia na chybu 404 a Google stratí prepojenie na indexované stránky – čo znamená pokles pozícií vo vyhľadávaní.

Skript tento problém rieši automaticky:

- Stiahne zoznam starých URL z histórie Wayback Machine a zo sitemáp
- Porovná ich s URL nového webu
- Vygeneruje hotové súbory pripravené na import do WordPressu

---

## Požiadavky

| Čo | Verzia / poznámka |
|---|---|
| Python | 3.8 alebo novší |
| Knižnica `requests` | inštaluje sa jedným príkazom |
| Internet | potrebný počas behu skriptu |
| WordPress | ľubovoľná verzia |
| Plugin Redirection alebo Rank Math Pro | podľa vašej voľby |

---

## Inštalácia Pythonu

Ak máte Python nainštalovaný, túto časť preskočte.

1. Otvorte [python.org/downloads](https://python.org/downloads)
2. Stiahnite najnovšiu verziu pre váš operačný systém
3. Spustite inštalátor

**Dôležité pri inštalácii na Windows:**  
Na prvej obrazovke inštalátora zaškrtnite možnosť **„Add Python to PATH"**. Bez toho príkaz `python` v termináli nebude fungovať.

Overenie inštalácie – otvorte terminál a zadajte:

```
python --version
```

Mali by ste vidieť výpis napríklad `Python 3.12.0`. Ak sa zobrazí chybová hláška, Python nie je správne nainštalovaný alebo nie je v PATH.

---

## Nastavenie vo Visual Studio Code

Visual Studio Code (VS Code) je bezplatný editor, ktorý vám umožní pracovať so skriptom, terminálom aj výstupnými súbormi na jednom mieste. Nie je povinný – skript môžete spúšťať aj v bežnom systémovom termináli – ale VS Code výrazne zjednodušuje prácu.

---

### Krok 1 – Inštalácia VS Code

1. Otvorte [code.visualstudio.com](https://code.visualstudio.com)
2. Stiahnite verziu pre váš operačný systém (Windows / macOS / Linux)
3. Spustite inštalátor a postupujte podľa sprievodcu

---

### Krok 2 – Inštalácia rozšírenia Python

Rozšírenie pridá do VS Code podporu Pythonu – zvýraznenie syntaxe, automatické dopĺňanie a výber interpreta.

1. Otvorte VS Code
2. Kliknite na ikonu **Extensions** v ľavom paneli (alebo stlačte `Ctrl+Shift+X` na Windows / `Cmd+Shift+X` na Mac)
3. Do vyhľadávacieho poľa zadajte `Python`
4. Kliknite na prvý výsledok – **Python** od spoločnosti Microsoft
5. Kliknite **Install**

---

### Krok 3 – Otvorenie priečinka projektu

1. Stiahnite súbory skriptu (`redirect_builder.py`) a uložte ich do jedného priečinka, napríklad `C:\projekty\redirect-builder` alebo `~/projekty/redirect-builder`
2. V menu VS Code zvoľte **File → Open Folder**
3. Nájdite a vyberte priečinok, kde máte uložený skript
4. VS Code otvorí celý priečinok – v ľavom paneli uvidíte všetky súbory projektu

---

### Krok 4 – Otvorenie terminálu vo VS Code

Namiesto systémového terminálu môžete používať terminál priamo vo VS Code – otvára sa automaticky v priečinku projektu.

```
Terminal → New Terminal
```

alebo klávesová skratka:

```
Ctrl+`    (Windows / Linux)
Cmd+`     (macOS)
```

Terminál sa otvorí v dolnej časti okna VS Code a je automaticky nastavený do priečinka projektu. Nemusíte manuálne navigovať pomocou príkazu `cd`.

---

### Krok 5 – Výber Python interpreta vo VS Code

VS Code potrebuje vedieť, ktorú verziu Pythonu má používať.

1. Stlačte `Ctrl+Shift+P` (Windows) alebo `Cmd+Shift+P` (macOS) – otvorí sa paleta príkazov
2. Zadajte `Python: Select Interpreter`
3. Zo zoznamu vyberte nainštalovanú verziu Pythonu (napr. `Python 3.12.0`)

Ak sa Python v zozname nezobrazuje, skontrolujte, či je správne nainštalovaný (pozri sekciu [Inštalácia Pythonu](#inštalácia-pythonu)).

---

### Krok 6 – Inštalácia knižnice requests

V termináli VS Code zadajte:

```
pip install requests
```

Ak príkaz `pip` nefunguje, vyskúšajte alternatívy:

```
pip3 install requests
```

alebo:

```
python -m pip install requests
```

Úspešná inštalácia vypíše niečo ako `Successfully installed requests-2.x.x`. Knižnicu stačí nainštalovať raz – pri ďalších spusteniach skriptu ju inštalovať znova netreba.

---

### Krok 7 – Overenie nastavenia

Skontrolujte, že všetko funguje správne:

```
python --version
python -c "import requests; print('requests OK')"
```

Ak oba príkazy prebehli bez chyby, môžete pokračovať.

---

## Prvé spustenie skriptu

Otvorte terminál vo VS Code (alebo systémový terminál v priečinku projektu) a zadajte jeden z nasledujúcich príkazov:

### Migrácia na novú doménu

```
python redirect_builder.py https://stary-web.sk https://novy-web.sk
```

### Zmena štruktúry URL na tej istej doméne

```
python redirect_builder.py https://web.sk https://web.sk
```

alebo jednoducho:

```
python redirect_builder.py https://web.sk
```

Skript sa opýta na adresu nového webu – ak je doména rovnaká, stlačte Enter.

---

### Čo skript robí počas behu

Po spustení skript vykonáva tieto kroky v poradí:

**1. Hľadanie sitemáp**  
Skript stiahne `robots.txt` a automaticky nájde URL sitemáp. Ak sitemap neexistuje, skript to oznámi a pokračuje ďalej.

**2. Sťahovanie URL z Wayback Machine**  
Skript kontaktuje CDX API Wayback Machine a stiahne historické URL starého webu. Pri weboch s tisíckami stránok to môže trvať 2–3 minúty. Terminál nevypínajte – skript beží na pozadí.

**3. Sťahovanie URL nového webu**  
Skript stiahne aktuálnu sitemap nového webu a zostaví zoznam cieľových URL.

**4. Porovnanie a generovanie CSV**  
Skript porovná staré a nové URL a vygeneruje súbor `redirects_PRACOVNY.csv`.

---

### Výpis počas behu – čo znamenajú hlášky

| Hláška | Čo sa deje |
|---|---|
| `Sťahujem sitemap...` | Skript načítava zoznam stránok nového webu |
| `Wayback Machine: sťahujem...` | Prebieha sťahovanie histórie – môže trvať dlhšie |
| `Sitemap nenájdená` | Web nemá sitemap – skript pokračuje ďalej cez Wayback Machine |
| `Hotovo. Vygenerovaný: redirects_PRACOVNY.csv` | Skript skončil, súbor je pripravený |

---

## Vyplnenie CSV súboru

Po skončení skriptu sa v priečinku projektu objaví súbor `redirects_PRACOVNY.csv`. Vo VS Code ho uvidíte hneď v ľavom paneli – kliknutím ho otvoríte.

Na pohodlné vyplnenie odporúčame otvoriť ho v **Microsoft Excel**, **Google Sheets** alebo **LibreOffice Calc**.

---

### Štruktúra CSV súboru

| Stĺpec | Obsah | Čo robiť |
|---|---|---|
| `source` | Stará URL (napr. `/o-nas/tym`) | Nemeňte – vyplnil skript automaticky |
| `destination` | Nová URL (napr. `/o-nas`) | **Toto musíte vyplniť** |
| `type` | Typ presmerovania (301) | Nemeňte |
| `note` | Poznámka | Môžete použiť pre vlastné poznámky |

---

### Ako vyplniť stĺpec destination

**Možnosť A – ručne**  
Otvorte CSV v tabuľkovom editore a ku každej starej URL doplňte zodpovedajúcu novú URL. Všetky URL zadávajte ako relatívne cesty (napr. `/nova-stranka/`) alebo absolútne URL (napr. `https://novy-web.sk/nova-stranka/`).

**Možnosť B – s pomocou AI (odporúčame)**  
Skopírujte obsah CSV do Claude alebo ChatGPT, priložte zoznam URL nového webu a napíšte:

> „Na základe starých URL v prvom stĺpci a zoznamu nových URL mi navrhni zodpovedajúce presmerovania. Zapíš ich do stĺpca destination."

AI navrhne mapovanie, vy skontrolujete a prípadne opravíte neisté riadky.

---

### Dôležité pravidlá pri vypĺňaní

- Každý riadok musí mať vyplnenú `destination` – riadky s prázdnou `destination` sa pri konverzii preskočia
- URL v stĺpci `destination` musí byť platná adresa na novom webe
- Neodstraňujte ani nepridávajte stĺpce – štruktúra CSV musí zostať zachovaná
- Súbor uložte pred spustením konvertora

---

## Konverzia do výstupných formátov

Keď máte vyplnený `redirects_PRACOVNY.csv`, spustite konvertor:

```
python redirect_builder.py --konvert https://novy-web.sk
```

Skript vygeneruje tri súbory naraz:

| Súbor | Použitie |
|---|---|
| `redirects_redirection_plugin.csv` | Import do pluginu Redirection |
| `redirects_rankmath_pro.csv` | Import do Rank Math Pro |
| `redirects.htaccess` | Priamy zápis do Apache servera |

Všetky tri súbory sa objavia v priečinku projektu – vo VS Code ich uvidíte v ľavom paneli.

---

## Import do WordPressu – plugin Redirection

Plugin **Redirection** je bezplatný, ľahko ovládateľný a odporúčame ho ako predvolený spôsob importu.

---

### Krok 1 – Inštalácia pluginu

1. Prihláste sa do WP Admin (napr. `https://novy-web.sk/wp-admin`)
2. Choďte na **Pluginy → Pridať nový**
3. Do vyhľadávacieho poľa zadajte `Redirection`
4. Nájdite plugin **Redirection** od autora **John Godley** (spravidla prvý výsledok)
5. Kliknite **Inštalovať**
6. Po dokončení inštalácie kliknite **Aktivovať**

---

### Krok 2 – Prvotné nastavenie pluginu

Po aktivácii plugin zobrazí sprievodcu nastavením:

1. Kliknite **Start Setup**
2. Na ďalšej obrazovke kliknite **Continue Setup**
3. Zvoľte, či chcete sledovať 404 chyby – odporúčame zapnúť
4. Kliknite **Finish Setup**

Plugin je teraz aktívny.

---

### Krok 3 – Import presmerovaní

1. Choďte na **Nástroje → Redirection** (alebo kliknite na **Redirection** v ľavom menu pod Nástrojmi)
2. Kliknite na záložku **Import/Export** v hornej časti stránky
3. V sekcii Import kliknite na tlačidlo **Choose file**
4. Nájdite a vyberte súbor `redirects_redirection_plugin.csv` zo svojho počítača
5. Kliknite **Upload file**
6. Plugin zobrazí náhľad importu – skontrolujte, že počet riadkov zodpovedá vášmu CSV
7. Kliknite **Import** alebo **Process**

---

### Krok 4 – Overenie importu

1. Choďte na záložku **Redirects**
2. Skontrolujte, že sa naimportované záznamy zobrazujú v zozname
3. Uistite sa, že všetky majú stav **Enabled** (zelené označenie)
4. Skontrolujte typ presmerovania – mal by byť **301**

---

## Import do WordPressu – Rank Math Pro

Rank Math Pro obsahuje vlastný modul Redirections s podporou importu CSV.

**Predpoklad:** Máte nainštalovaný a aktivovaný plugin **Rank Math SEO Pro**.

---

### Krok 1 – Otvorenie modulu Redirections

1. Prihláste sa do WP Admin
2. V ľavom menu kliknite na **Rank Math**
3. Zvoľte **Redirections**

Ak sa Redirections v menu nezobrazuje, skontrolujte, či je modul zapnutý: **Rank Math → Dashboard → Modules → Redirections → Zapnúť**.

---

### Krok 2 – Import CSV súboru

1. V pravom hornom rohu stránky Redirections kliknite na tlačidlo **Import**
2. Zobrazí sa dialógové okno na výber súboru
3. Kliknite **Choose file** a vyberte `redirects_rankmath_pro.csv` zo svojho počítača
4. Kliknite **Import**
5. Rank Math zobrazí hlášku s počtom naimportovaných záznamov

---

### Krok 3 – Overenie importu

1. V zozname Redirections skontrolujte naimportované záznamy
2. Uistite sa, že záznamy majú stav **Active**
3. Skontrolujte, že typ presmerovania je nastavený na **301** (trvalé presmerovanie)

**Poznámka k typom presmerovaní:**  
Pre migráciu webu vždy používajte **301 – trvalé presmerovanie**. Tento typ informuje Google, že stránka sa trvalo presunula, a prenáša PageRank (autoritu stránky) na novú URL. Typ 302 (dočasné presmerovanie) autoritu neprenáša – používa sa iba vtedy, keď je presmerovanie skutočne dočasné.

---

## Overenie presmerovaní

Po importe odporúčame otestovať niekoľko presmerovaní skôr, než ich zverejníte alebo oznámite Googlu.

### Ručné testovanie v prehliadači

1. Skopírujte niektorú zo starých URL (zo stĺpca `source` v CSV)
2. Vlepte ju do adresného riadka prehliadača a stlačte Enter
3. Prehliadač by mal automaticky prejsť na novú URL (stĺpec `destination`)
4. Skontrolujte, že cieľová stránka sa načíta správne a URL v adresnom riadku je nová

### Testovanie pomocou nástroja

Môžete použiť bezplatný nástroj [httpstatus.io](https://httpstatus.io) alebo [redirect-checker.org](https://redirect-checker.org):

1. Vlepte niekoľko starých URL
2. Spustite kontrolu
3. Skontrolujte, že každá URL vracia status **301** a správnu cieľovú adresu

### Čo robiť, ak presmerovanie nefunguje

- Overte, že plugin Redirection alebo Rank Math je aktívny
- Skontrolujte, že importovaný záznam má stav Enabled / Active
- Skontrolujte, že stará URL v zázname sa zhoduje s tou, ktorú testujete (vrátane lomky na konci)
- Skontrolujte, či nie je na webe iné pravidlo, ktoré dané presmerovanie prepisuje (napr. v `.htaccess`)

---

## Monitorovanie po spustení

Po spustení nového webu sa môže stať, že niektoré URL chýbajú v presmerovaniach – napríklad stránky, ktoré Wayback Machine nemala v histórii.

### Zapnutie monitora 404 chýb

**Cez plugin Redirection:**

1. WP Admin → Nástroje → Redirection
2. Záložka **Log**
3. Skontrolujte, či je zapnuté logovanie – ak nie, choďte do **Options** a zapnite **Log 404 Errors**

**Cez Rank Math (bezplatná verzia):**

1. WP Admin → Rank Math → General Settings
2. Záložka **404 Monitor**
3. Prepnite na **ON**

### Postup po týždni prevádzky

1. Otvorte log 404 chýb (Redirection → Log alebo Rank Math → 404 Monitor)
2. Skontrolujte adresy, ktoré návštevníci alebo Google navštívili a nenašli
3. Pre každú relevantnú adresu pridajte presmerovanie ručne alebo zopakujte celý postup s novou sadou URL
4. Ignorujte zjavne chybné alebo nesúvisiace URL (napr. pokusy o útok, náhodné URL)

---

## Časté problémy a riešenia

---

**„pip nie je rozpoznaný príkaz"**

Vyskúšajte alternatívy v tomto poradí:

```
pip3 install requests
python -m pip install requests
python3 -m pip install requests
```

Ak ani jedna z možností nefunguje, Python pravdepodobne nie je v PATH. Preinštalujte Python a na prvej obrazovke inštalátora zaškrtnite **„Add Python to PATH"**.

---

**„python nie je rozpoznaný príkaz" na Windows**

Na niektorých systémoch treba namiesto `python` používať `py`:

```
py redirect_builder.py https://stary-web.sk https://novy-web.sk
```

---

**Wayback Machine beží veľmi dlho**

Je to normálne pri weboch s tisíckami URL. Skript beží – nevypínajte terminál. Pri weboch s 1 000 a viac stránkami môže sťahovanie trvať aj 5–10 minút.

---

**Sitemap sa nenašla**

Skript to oznámi a pokračuje ďalej cez Wayback Machine. Ak chcete doplniť URL nového webu manuálne:

1. Vytvorte textový súbor `novy_web_urls.txt` v priečinku projektu
2. Na každý riadok vlepte jednu URL nového webu
3. Spustite skript znova – automaticky použije tento súbor

---

**CSV súbor sa otvoril, ale stĺpce sú pomiešané**

Pri otváraní v Exceli nastavte oddeľovač na čiarku. Postup:

1. Otvorte Excel → Dáta → Zo súboru → Z textu/CSV
2. Ako oddeľovač zvoľte **Čiarka**
3. Kliknite **Načítať**

---

**VS Code nevidí Python**

1. Stlačte `Ctrl+Shift+P` (Windows) alebo `Cmd+Shift+P` (macOS)
2. Zadajte `Python: Select Interpreter`
3. Zo zoznamu vyberte nainštalovanú verziu Pythonu

Ak sa Python v zozname nezobrazuje, skontrolujte, či je nainštalovaný príkazom `python --version` v systémovom termináli.

---

**Import do pluginu Redirection zlyhá**

Skontrolujte, že CSV má správne hlavičky v prvom riadku:

```
source,destination,type
```

Hlavičky musia byť presne takto zapísané – malými písmenami, bez medzier. Ak sú inak pomenované, plugin import odmietne.

---

**Po importe presmerovania nefungujú**

Skontrolujte v tomto poradí:

1. Je plugin Redirection / Rank Math **aktivovaný**?
2. Majú záznamy stav **Enabled / Active**?
3. Zhodujú sa URL v zázname s reálnymi starými adresami (vrátane lomky na konci)?
4. Nie je v súbore `.htaccess` konfliktné pravidlo?

---

**Chcem len formát pre Rank Math Pro**

Všetky tri výstupné súbory sa generujú vždy naraz. Použite `redirects_rankmath_pro.csv` a ostatné súbory ignorujte.

---

## Podpora

Ak niečo nefunguje, otvorte Issue na GitHube a priložte:

- Verziu Pythonu: výstup príkazu `python --version`
- Chybovú hlášku: skopírujte celý výstup z terminálu
- Doménu webu (ak je verejne dostupná)
