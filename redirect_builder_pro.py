"""
Redirect Builder Pro  –  Tavily + Gemini (plna automatizacia)
=============================================================
Spustenie:
    python redirect_builder_pro.py https://stary-web.sk https://novy-web.sk
    python redirect_builder_pro.py https://stary-web.sk       # novy = rovnaka domena
    python redirect_builder_pro.py                            # opyta sa interaktivne

Konverzia (ak si upravil CSV):
    python redirect_builder_pro.py --konvert
    python redirect_builder_pro.py --konvert https://novy-web.sk

Zdroje URL (v tomto poradi, vysledky sa spajaju):
    1. robots.txt  ->  sitemap (automaticka detekcia)
    2. Wayback Machine CDX API
    3. Tavily Search API  (aktualne indexovane Google stranky)

AI mapovanie:
    Gemini Flash  ->  navrhne destination pre kazdy stary path
    Nistota vystupu:
        [OK]   ->  vysoka istota, rovno do CSV
        [?]    ->  stredna istota, odporuca sa skontrolovat
        [??]   ->  nizka istota, vyzaduje manualnu kontrolu

API kluce:
    TAVILY_API_KEY  –  tavily.com/account/api-keys  (1000 kreditov zadarmo/mesiac)
    GEMINI_API_KEY  –  aistudio.google.com/apikey    (zadarmo, Gemini 2.0 Flash)

Nastavenie API klucov:
    Moznost A: priamo v tomto subore (TAVILY_API_KEY, GEMINI_API_KEY nizsie)
    Moznost B: premenne prostredia
               Windows:   set TAVILY_API_KEY=tvoj_kluc
               Mac/Linux: export TAVILY_API_KEY=tvoj_kluc

Vystupy po --konvert:
    redirects_redirection_plugin.csv   (plugin Redirection – zadarmo)
    redirects.htaccess                 (priamy Apache)
    redirects_rankmath_pro.csv         (Rank Math Pro)
"""

import csv
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests

# ----------------------------------------------------------
# API KLUCE  –  nastav tu alebo cez premenne prostredia
# ----------------------------------------------------------

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ----------------------------------------------------------
# NASTAVENIA
# ----------------------------------------------------------

HARDCODED_STARA = ""
HARDCODED_NOVA  = ""

PRACOVNY_CSV    = "redirects_PRACOVNY.csv"

TAVILY_MAX_RESULTS_PER_QUERY = 20
TAVILY_QUERY_VARIANTS        = 5   # pocet roznych dopytov pre vacsiu pokrytost
GEMINI_CHUNK_SIZE            = 80  # pocet URL na jeden API volanie

SKIP_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".css", ".js", ".ico", ".pdf", ".xml", ".json",
    ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3",
    ".zip", ".gz", ".gpx", ".rar", ".doc", ".docx",
    ".txt", ".map",
)

SKIP_SEGMENTS = (
    "/wp-content/", "/wp-includes/", "/wp-json/",
    "/feed", "/atom.xml", "/index.xml", "/.well-known/",
    "/elementor/", "/sitemap", "/wlwmanifest", "/embed/",
    "/tag/", "/category/", "/author/", "/kategoria/",
)

# ----------------------------------------------------------
# POMOCNE FUNKCIE
# ----------------------------------------------------------

def header(text):
    print(f"\n  {text}")
    print(f"  {'─' * len(text)}")


def ok(text):
    print(f"  ✓ {text}")


def warn(text):
    print(f"  ! {text}")


def err(text):
    print(f"  x {text}")


def info(text):
    print(f"    {text}")


def clean_domain(raw):
    d = raw.lower().strip()
    d = d.replace("https://", "").replace("http://", "")
    d = d.replace("www.", "").rstrip("/")
    return d


def is_valid_url(url):
    if "?" in url or "#" in url:
        return False
    url_lower = url.lower()
    for ext in SKIP_EXTENSIONS:
        if url_lower.endswith(ext):
            return False
    for seg in SKIP_SEGMENTS:
        if seg in url:
            return False
    return True


def extract_path(url):
    try:
        path = urlparse(url).path
        if path and not path.endswith("/") and "." not in path.split("/")[-1]:
            path += "/"
        return path if path and path != "/" else None
    except Exception:
        return None


def classify_path(path):
    p = path.lower()
    if "registraci" in p:
        return "REGISTRACIA"
    if "vysledky" in p or "výsledky" in p:
        return "VYSLEDKY"
    if "zoznam-prihlasenych" in p:
        return "ZOZNAM_PRIHLASENYCH"
    if "podujati" in p:
        return "PODUJATIA"
    if "blog" in p or p.count("/") >= 4:
        return "BLOG_CLANKY"
    return "OSTATNE"

# ----------------------------------------------------------
# VSTUP
# ----------------------------------------------------------

def get_domains():
    print()
    print("  Redirect Builder Pro  –  Tavily + Gemini")
    print("  ==========================================")

    if TAVILY_API_KEY:
        ok("Tavily API key nastaven")
    else:
        warn("Tavily API key chyba – URL discovery bez neho (len Wayback + sitemap)")

    if GEMINI_API_KEY:
        ok("Gemini API key nastaven")
    else:
        warn("Gemini API key chyba – mapovanie bude manualné (rovnako ako zakladna verzia)")

    if len(sys.argv) >= 3 and not sys.argv[1].startswith("--"):
        stara = clean_domain(sys.argv[1])
        nova  = clean_domain(sys.argv[2])

    elif len(sys.argv) == 2 and not sys.argv[1].startswith("--"):
        stara = clean_domain(sys.argv[1])
        print(f"\n  Stary web z argumentu : {stara}")
        raw_nova = input("  Novy web URL (Enter = rovnaka domena): ").strip()
        nova = clean_domain(raw_nova) if raw_nova else stara

    else:
        default_stara = HARDCODED_STARA or "(zadaj)"
        default_nova  = HARDCODED_NOVA  or "(zadaj)"
        print(f"\n  Stary web (Enter = {default_stara}):")
        raw_stara = input("  > ").strip()
        stara = clean_domain(raw_stara) if raw_stara else clean_domain(HARDCODED_STARA)

        print(f"\n  Novy web  (Enter = {default_nova}):")
        raw_nova = input("  > ").strip()
        nova = clean_domain(raw_nova) if raw_nova else (clean_domain(HARDCODED_NOVA) if HARDCODED_NOVA else stara)

    if not stara:
        err("Nezadal si ziadnu domenu.")
        sys.exit(1)
    if not nova:
        nova = stara

    print(f"\n  Stary web : https://{stara}")
    print(f"  Novy web  : https://{nova}")
    return stara, nova

# ----------------------------------------------------------
# KROK 1a: robots.txt  ->  sitemap
# ----------------------------------------------------------

def discover_sitemaps_from_robots(domain):
    for url in [f"https://{domain}/robots.txt", f"https://www.{domain}/robots.txt"]:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                found = []
                for line in resp.text.splitlines():
                    if line.lower().startswith("sitemap:"):
                        found.append(line.split(":", 1)[1].strip())
                if found:
                    ok(f"robots.txt: {len(found)} sitemap URL")
                    return found
        except Exception:
            pass
    return []


def parse_sitemap_xml(content, domain, depth=0):
    if depth > 3:
        return set()

    paths = set()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        warn(f"XML parse chyba: {e}")
        return paths

    sub_sitemaps = root.findall(".//sm:sitemap/sm:loc", ns)
    if sub_sitemaps:
        info(f"sitemap index – {len(sub_sitemaps)} pod-sitemaps:")
        for sub in sub_sitemaps:
            sub_url = sub.text.strip()
            try:
                r = requests.get(sub_url, timeout=20)
                if r.status_code == 200:
                    sub_paths = parse_sitemap_xml(r.content, domain, depth + 1)
                    name = sub_url.split("/")[-1]
                    info(f"  {name:<45} {len(sub_paths):>4} URL")
                    paths.update(sub_paths)
            except Exception as e:
                warn(f"  {sub_url}  ->  {e}")
    else:
        for loc in root.findall(".//sm:url/sm:loc", ns):
            text = loc.text
            if text:
                p = extract_path(text.strip())
                if p and is_valid_url(text):
                    paths.add(p)

    return paths


def fetch_sitemap_urls(domain, label="web"):
    header(f"Sitemap  –  {domain}  ({label})")

    robots_sitemaps = discover_sitemaps_from_robots(domain)
    candidates = robots_sitemaps + [
        f"https://{domain}/sitemap_index.xml",
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/wp-sitemap.xml",
        f"https://www.{domain}/sitemap.xml",
    ]

    seen = set()
    for sitemap_url in candidates:
        if sitemap_url in seen:
            continue
        seen.add(sitemap_url)
        try:
            info(f"Skusam: {sitemap_url}")
            resp = requests.get(sitemap_url, timeout=30)
            if resp.status_code != 200:
                continue
            paths = parse_sitemap_xml(resp.content, domain)
            if paths:
                ok(f"Celkom URL zo sitemáp: {len(paths)}")
                return paths
        except Exception as e:
            warn(f"{sitemap_url}  ->  {e}")

    warn("Sitemap nenajdena.")
    info("Fallback: vytvor 'novy_web_urls.txt' (1 URL = 1 riadok) a spusti znova.")

    if os.path.exists("novy_web_urls.txt"):
        paths = set()
        with open("novy_web_urls.txt", encoding="utf-8") as f:
            for line in f:
                p = extract_path(line.strip())
                if p:
                    paths.add(p)
        ok(f"Manualny subor: {len(paths)} URL")
        return paths

    return set()

# ----------------------------------------------------------
# KROK 2: Wayback Machine
# ----------------------------------------------------------

def fetch_wayback(domain, retries=3):
    header(f"Wayback Machine CDX API  –  {domain}")

    api_url = (
        f"https://web.archive.org/cdx/search/cdx"
        f"?url={domain}/*&output=json&fl=original&collapse=urlkey&limit=100000"
    )
    info(api_url)

    for attempt in range(1, retries + 1):
        try:
            info(f"Pokus {attempt}/{retries}...")
            resp = requests.get(api_url, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                urls = [row[0] for row in data[1:]]
                ok(f"Stiahnutych URL: {len(urls)}")
                return urls
            elif resp.status_code == 429:
                warn("Rate limit – cakam 30s...")
                time.sleep(30)
            else:
                warn(f"HTTP {resp.status_code}")
                time.sleep(5)
        except requests.Timeout:
            warn(f"Timeout (pokus {attempt}/{retries}) – cakam 10s...")
            time.sleep(10)
        except Exception as e:
            err(f"Chyba: {e}")

    warn("Wayback Machine nedostupna alebo domena nie je archivovana.")
    return []

# ----------------------------------------------------------
# KROK 3: Tavily Search API
# ----------------------------------------------------------

def fetch_tavily_urls(domain):
    header(f"Tavily Search API  –  {domain}")

    if not TAVILY_API_KEY:
        warn("TAVILY_API_KEY nie je nastaveny – preskakujem.")
        info("Nastav ho v subore alebo cez:  export TAVILY_API_KEY=tvoj_kluc")
        return []

    # Rozne query varianty pre vacsiu pokrytost
    queries = [domain]
    for i in range(1, TAVILY_QUERY_VARIANTS):
        queries.append(f"{domain} stranky")

    all_urls = []
    seen     = set()

    for i, query in enumerate(queries[:TAVILY_QUERY_VARIANTS], 1):
        try:
            info(f"Query {i}/{TAVILY_QUERY_VARIANTS}: {query}")
            payload = {
                "api_key":        TAVILY_API_KEY,
                "query":          query,
                "include_domains": [domain, f"www.{domain}"],
                "max_results":    TAVILY_MAX_RESULTS_PER_QUERY,
                "search_depth":   "basic",
            }
            resp = requests.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=30,
            )
            if resp.status_code == 401:
                err("Tavily: neplatny API kluc.")
                return []
            if resp.status_code == 429:
                warn("Tavily: rate limit – cakam 10s...")
                time.sleep(10)
                continue
            if resp.status_code != 200:
                warn(f"Tavily: HTTP {resp.status_code}")
                continue

            data = resp.json()
            results = data.get("results", [])
            new_count = 0
            for r in results:
                url = r.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    all_urls.append(url)
                    new_count += 1
            info(f"  -> {new_count} novych URL (celkom: {len(all_urls)})")
            time.sleep(0.5)

        except Exception as e:
            warn(f"Tavily query {i}: {e}")

    ok(f"Tavily celkom: {len(all_urls)} URL")
    return all_urls

# ----------------------------------------------------------
# KROK 4: Filter a porovnanie
# ----------------------------------------------------------

def filter_old_urls(wayback_urls, tavily_urls, sitemap_paths):
    header("Filtrovanie URL stareho webu")

    all_urls = list(wayback_urls) + list(tavily_urls) + [f"/{p.lstrip('/')}" for p in sitemap_paths]
    info(f"Celkom pred filtrom : {len(all_urls)}")

    paths   = set()
    skipped = 0
    for url in all_urls:
        if is_valid_url(url):
            p = extract_path(url)
            if p:
                paths.add(p)
        else:
            skipped += 1

    info(f"Preskocených        : {skipped}")
    ok(f"Cistych stranok     : {len(paths)}")
    return paths


def compare_urls(old_paths, new_paths):
    header("Porovnanie  stary <-> novy web")

    if not new_paths:
        warn("Ziadne URL noveho webu – vsetky stare pujdu do 'potrebuje redirect'.")
        return set(), sorted(old_paths), []

    zachovane          = set()
    potrebuje_redirect = set()

    for path in old_paths:
        if path in new_paths:
            zachovane.add(path)
        else:
            potrebuje_redirect.add(path)

    nove_len = len(new_paths - old_paths)

    print()
    ok(f"URL zachovane (zhodne na novom webe)  : {len(zachovane)}")
    info(  "  -> ziadny redirect nepotrebny")
    ok(f"URL potrebujuce redirect              : {len(potrebuje_redirect)}")
    info(  "  -> Gemini navrhne mapovanie")
    info(f"URL iba na novom webe               : {nove_len}")

    return zachovane, sorted(potrebuje_redirect), sorted(new_paths - old_paths)

# ----------------------------------------------------------
# KROK 5: Gemini Auto-mapovanie
# ----------------------------------------------------------

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def gemini_request(prompt):
    if not GEMINI_API_KEY:
        return None

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096},
    }
    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=60,
        )
        if resp.status_code == 401:
            err("Gemini: neplatny API kluc.")
            return None
        if resp.status_code == 429:
            warn("Gemini: rate limit – cakam 15s...")
            time.sleep(15)
            return gemini_request(prompt)
        if resp.status_code != 200:
            warn(f"Gemini: HTTP {resp.status_code}")
            return None

        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        warn(f"Gemini chyba: {e}")
        return None


def auto_map_with_gemini(potrebuje_redirect, new_paths):
    header("Gemini Auto-mapovanie  source -> destination")

    if not GEMINI_API_KEY:
        warn("GEMINI_API_KEY nie je nastaveny – preskakujem auto-mapovanie.")
        info("Nastav ho v subore alebo cez:  export GEMINI_API_KEY=tvoj_kluc")
        return {path: ("", "??") for path in potrebuje_redirect}

    new_paths_list = sorted(new_paths)
    sources        = list(potrebuje_redirect)
    mappings       = {}

    total_chunks = (len(sources) + GEMINI_CHUNK_SIZE - 1) // GEMINI_CHUNK_SIZE
    info(f"Celkom URL na mapovatl: {len(sources)}  |  Chunk size: {GEMINI_CHUNK_SIZE}  |  Pocet volaní: {total_chunks}")

    for chunk_idx in range(total_chunks):
        chunk = sources[chunk_idx * GEMINI_CHUNK_SIZE : (chunk_idx + 1) * GEMINI_CHUNK_SIZE]

        prompt = f"""Si asistent pre migráciu webstranky. Tvojou ulohou je priradit stare URL k najvhodnejsim novym URL.

STARE URL (potrebuju redirect):
{chr(10).join(chunk)}

DOSTUPNE NOVE URL (mozne destinacie):
{chr(10).join(new_paths_list[:200])}

Pravidla:
- Prirad kazde stare URL k najvhodnejsiemu novemu URL.
- Ak neexistuje vhodna zhoda, pouzi  /
- confidence: "high" = jasna zhoda, "medium" = pravdepodobna zhoda, "low" = hádané

Odpovedaj IBA validnym JSON v tomto formate (bez markdown, bez komentovania):
{{"mappings": [{{"source": "/old-path/", "destination": "/new-path/", "confidence": "high"}}]}}"""

        info(f"Chunk {chunk_idx + 1}/{total_chunks}  ({len(chunk)} URL)...")
        raw = gemini_request(prompt)

        if not raw:
            for path in chunk:
                mappings[path] = ("", "??")
            continue

        try:
            clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data  = json.loads(clean)
            for item in data.get("mappings", []):
                src  = item.get("source", "")
                dest = item.get("destination", "")
                conf = item.get("confidence", "low")

                if conf == "high":
                    marker = "[OK]"
                elif conf == "medium":
                    marker = "[?]"
                else:
                    marker = "[??]"

                mappings[src] = (dest, marker)

        except json.JSONDecodeError as e:
            warn(f"Chunk {chunk_idx + 1}: JSON parse chyba ({e}) – chunk preskoceny, treba manualnu kontrolu.")
            for path in chunk:
                mappings[path] = ("", "??")

        time.sleep(1)

    mapped_ok  = sum(1 for d, m in mappings.values() if m == "[OK]")
    mapped_mid = sum(1 for d, m in mappings.values() if m == "[?]")
    mapped_low = sum(1 for d, m in mappings.values() if m in ("[??]", "??"))

    print()
    ok(f"Vysoka istota  [OK]  : {mapped_ok}")
    warn(f"Stredna istota [?]   : {mapped_mid}  (odporuca sa skontrolovat)")
    warn(f"Nizka istota   [??]  : {mapped_low}  (vyzaduje manualnu kontrolu)")

    return mappings

# ----------------------------------------------------------
# KROK 6: Generovanie pracovneho CSV
# ----------------------------------------------------------

def create_working_csv(zachovane, potrebuje_redirect, stara_domain, mappings=None):
    header("Generovanie pracovneho CSV")

    info_file = f"{stara_domain.replace('.', '_')}_zachovane.txt"
    with open(info_file, "w", encoding="utf-8") as f:
        f.write("# URL zachovane – rovnake na starom aj novom webe\n")
        f.write("# Tieto stranky NEPOTREBUJU redirect.\n\n")
        for path in sorted(zachovane):
            f.write(path + "\n")
    ok(f"Zachovane URL (info) : {info_file}")

    groups = {
        "REGISTRACIA":         [],
        "VYSLEDKY":            [],
        "ZOZNAM_PRIHLASENYCH": [],
        "PODUJATIA":           [],
        "BLOG_CLANKY":         [],
        "OSTATNE":             [],
    }
    for path in potrebuje_redirect:
        groups[classify_path(path)].append(path)

    total = 0
    with open(PRACOVNY_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if mappings:
            writer.writerow(["# Gemini navrhol mapovanie.", "", "", ""])
            writer.writerow(["# [OK]=vysoka istota | [?]=skontrolovat | [??]=manualná kontrola", "", "", ""])
        else:
            writer.writerow(["# Postup: dopln stlpec 'destination' pre kazdy riadok.", "", "", ""])

        writer.writerow(["# Potom spusti:  python redirect_builder_pro.py --konvert", "", "", ""])
        writer.writerow(["source", "destination", "type", "note"])

        for group_name, group_paths in groups.items():
            if group_paths:
                writer.writerow([f"# === {group_name} ({len(group_paths)}) ===", "", "", ""])
                for path in sorted(group_paths):
                    if mappings and path in mappings:
                        dest, marker = mappings[path]
                    else:
                        dest, marker = "", ""
                    writer.writerow([path, dest, "301", marker])
                    total += 1

    ok(f"Pracovny CSV ({total} redirectov) : {PRACOVNY_CSV}")
    print()
    info("Rozdelenie do skupin:")
    for g, p in groups.items():
        if p:
            info(f"  {g:<25} {len(p):>4} URL")

    return PRACOVNY_CSV, info_file

# ----------------------------------------------------------
# FAZA 2: Konvertor
# ----------------------------------------------------------

def load_filled_csv(filepath):
    redirects       = []
    skipped_empty   = 0
    skipped_comment = 0

    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue

            source      = row[0].strip()
            destination = row[1].strip() if len(row) > 1 else ""
            code        = row[2].strip() if len(row) > 2 else "301"

            if source.startswith("#") or source == "source":
                skipped_comment += 1
                continue

            if not destination:
                skipped_empty += 1
                continue

            if not destination.startswith("/") and not destination.startswith("http"):
                destination = "/" + destination

            if not code.isdigit():
                code = "301"

            redirects.append({"source": source, "destination": destination, "code": code})

    return redirects, skipped_empty, skipped_comment


def export_redirection_plugin(redirects, output_file):
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "code"])
        for r in redirects:
            writer.writerow([r["source"], r["destination"], r["code"]])
    ok(f"Redirection plugin CSV ({len(redirects)} riadkov) : {output_file}")


def export_htaccess(redirects, output_file, nova_domain):
    lines = [
        "# ============================================================",
        "# Redirecty – vygenerovane redirect_builder_pro.py",
        "# Vloz PRED blok:  # BEGIN WordPress",
        "# ============================================================",
        "",
        "RewriteEngine On",
        "",
    ]
    current_group = None
    for r in redirects:
        group = classify_path(r["source"])
        if group != current_group:
            if current_group is not None:
                lines.append("")
            lines.append(f"# --- {group} ---")
            current_group = group

        src  = re.escape(r["source"].lstrip("/")).replace(r"\/", "/")
        dest = r["destination"]
        code = r["code"]

        if dest.startswith("/"):
            dest = f"https://{nova_domain}{dest}"

        lines.append(f"RewriteRule ^{src}?$ {dest} [R={code},L]")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    ok(f".htaccess snippet ({len(redirects)} pravidiel) : {output_file}")


def export_rankmath_csv(redirects, output_file):
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination", "type"])
        for r in redirects:
            writer.writerow([r["source"], r["destination"], r["code"]])
    ok(f"Rank Math Pro CSV ({len(redirects)} riadkov)   : {output_file}")


def run_konvertor(nova_domain):
    print()
    print("  Redirect Builder Pro  –  konvertor (Faza 2)")
    print("  =============================================")
    info(f"Nacitavam: {PRACOVNY_CSV}")
    print()

    if not os.path.exists(PRACOVNY_CSV):
        err(f"Subor '{PRACOVNY_CSV}' nenajdeny.")
        info("Najprv spusti skript bez --konvert.")
        sys.exit(1)

    redirects, skipped_empty, skipped_comment = load_filled_csv(PRACOVNY_CSV)

    info(f"Nacitanych redirectov    : {len(redirects)}")
    if skipped_empty:
        warn(f"Prazdna destination      : {skipped_empty}  (preskocene – este doplnit!)")
    info(f"Komentare / hlavicky     : {skipped_comment}  (OK)")

    if not redirects:
        warn("Ziadne redirecty s vyplnenou destination.")
        print()
        info(f"1. Otvor '{PRACOVNY_CSV}' v Exceli / Google Sheets.")
        info("2. Doplnit stlpec 'destination'.")
        info("3. Uloz a spusti znova:  python redirect_builder_pro.py --konvert")
        sys.exit(1)

    header("Generovanie vystupnych suborov")
    print()

    export_redirection_plugin(redirects, "redirects_redirection_plugin.csv")
    export_htaccess(redirects, "redirects.htaccess", nova_domain)
    export_rankmath_csv(redirects, "redirects_rankmath_pro.csv")

    print()
    print("  Vyberte si JEDEN sposob importu:")
    print()
    print("  [1]  Plugin Redirection  (zadarmo – odporucane)")
    print("       Subor  : redirects_redirection_plugin.csv")
    print("       Plugin : wordpress.org/plugins/redirection")
    print("       Kde    : WP Admin -> Redirection -> Import/Export -> Import from CSV")
    print()
    print("  [2]  .htaccess  (bez pluginu, Apache)")
    print("       Subor  : redirects.htaccess")
    print("       Kde    : Vloz obsah PRED  # BEGIN WordPress  v .htaccess")
    print()
    print("  [3]  Rank Math Pro")
    print("       Subor  : redirects_rankmath_pro.csv")
    print("       Kde    : Rank Math -> Redirections -> Import")
    print()
    info("Po spusteni webu: Rank Math (free) -> General Settings -> 404 Monitor -> ON")
    print()

# ----------------------------------------------------------
# HLAVNY PROGRAM
# ----------------------------------------------------------

def main():
    if "--konvert" in sys.argv:
        if HARDCODED_NOVA:
            nova = clean_domain(HARDCODED_NOVA)
        else:
            nova_arg = next(
                (a for a in sys.argv[1:] if not a.startswith("--")),
                None
            )
            if nova_arg:
                nova = clean_domain(nova_arg)
            else:
                raw = input("\n  Novy web URL: ").strip()
                nova = clean_domain(raw) if raw else ""
        if not nova:
            err("Nezadal si URL noveho webu.")
            sys.exit(1)
        run_konvertor(nova)
        return

    stara, nova = get_domains()

    # Zbieranie URL stareho webu
    old_sitemap_paths = fetch_sitemap_urls(stara, "stary web")
    wayback_urls      = fetch_wayback(stara)
    tavily_urls       = fetch_tavily_urls(stara)

    if not wayback_urls and not tavily_urls and not old_sitemap_paths:
        err("Ziadne URL stareho webu. Skontroluj domenu a sietove pripojenie.")
        sys.exit(1)

    # Zbieranie URL noveho webu
    new_paths = fetch_sitemap_urls(nova, "novy web")

    # Spracovanie
    old_paths = filter_old_urls(wayback_urls, tavily_urls, old_sitemap_paths)
    zachovane, potrebuje_redirect, nove = compare_urls(old_paths, new_paths)

    # AI mapovanie
    mappings = auto_map_with_gemini(potrebuje_redirect, new_paths) if GEMINI_API_KEY else None

    csv_file, info_file = create_working_csv(zachovane, potrebuje_redirect, stara, mappings)

    print()
    if GEMINI_API_KEY:
        print("  Gemini navrhol mapovanie. Dalsi postup:")
        print()
        info(f"1. Otvor '{csv_file}' v Exceli alebo Google Sheets.")
        info("2. Skontroluj riadky oznacene [?] a [??].")
        info("3. Oprav alebo doplnaj destination kde treba.")
        info(f"4. Uloz subor – rovnaky nazov: {csv_file}")
        info("5. Spusti konvertor:")
        info("   python redirect_builder_pro.py --konvert https://novy-web.sk")
    else:
        print("  Faza 1 hotova. Dalsi postup:")
        print()
        info(f"1. Otvor '{csv_file}' v Exceli alebo Google Sheets.")
        info("2. Dopln stlpec 'destination'.")
        info("3. Uloz a spusti:")
        info("   python redirect_builder_pro.py --konvert https://novy-web.sk")

    print()
    info(f"URL bez redirectu (zachovane): {info_file}")
    print()


if __name__ == "__main__":
    main()
