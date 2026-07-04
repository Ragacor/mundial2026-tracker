#!/usr/bin/env python3
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path
from datetime import datetime, timezone

COLLECTION_URL = "https://www.rtve.es/play/colecciones/mundial-2026-resumenes/4735/"
SEARCH_URL = "https://www.rtve.es/buscador/?q="
OPENFOOTBALL_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "videos-rtve.json"

TEAM_VARIANTS = {
    "Algeria": ["algeria", "argelia"],
    "Argentina": ["argentina"],
    "Australia": ["australia"],
    "Austria": ["austria"],
    "Belgium": ["belgium", "belgica", "bélgica"],
    "Bosnia and Herzegovina": ["bosnia", "bosnia herzegovina", "bosnia y herzegovina", "bosnia and herzegovina"],
    "Brazil": ["brazil", "brasil"],
    "Canada": ["canada", "canadá"],
    "Cape Verde": ["cape verde", "cabo verde"],
    "Colombia": ["colombia"],
    "Croatia": ["croatia", "croacia"],
    "Curacao": ["curacao", "curazao", "curaçao"],
    "Ecuador": ["ecuador"],
    "Egypt": ["egypt", "egipto"],
    "England": ["england", "inglaterra"],
    "France": ["france", "francia"],
    "Germany": ["germany", "alemania"],
    "Ghana": ["ghana"],
    "Haiti": ["haiti", "haití"],
    "Iran": ["iran", "irán"],
    "Ivory Coast": ["ivory coast", "costa de marfil"],
    "Japan": ["japan", "japon", "japón"],
    "Mexico": ["mexico", "méxico"],
    "Morocco": ["morocco", "marruecos"],
    "Netherlands": ["netherlands", "paises bajos", "países bajos", "holanda"],
    "New Zealand": ["new zealand", "nueva zelanda"],
    "Norway": ["norway", "noruega"],
    "Paraguay": ["paraguay"],
    "Portugal": ["portugal"],
    "Qatar": ["qatar"],
    "Saudi Arabia": ["saudi arabia", "arabia saudi", "arabia saudí"],
    "Scotland": ["scotland", "escocia"],
    "Senegal": ["senegal"],
    "South Africa": ["south africa", "sudafrica", "sudáfrica"],
    "Spain": ["spain", "espana", "españa"],
    "Sweden": ["sweden", "suecia"],
    "Switzerland": ["switzerland", "suiza"],
    "Tunisia": ["tunisia", "tunez", "túnez"],
    "Turkey": ["turkey", "turquia", "turquía"],
    "United States": ["united states", "usa", "estados unidos", "eeuu", "ee uu"],
    "Uruguay": ["uruguay"]
}

# Preferred Spanish names for RTVE search queries
TEAM_ES = {
    "Algeria": "Argelia",
    "Argentina": "Argentina",
    "Australia": "Australia",
    "Austria": "Austria",
    "Belgium": "Bélgica",
    "Bosnia and Herzegovina": "Bosnia",
    "Brazil": "Brasil",
    "Canada": "Canadá",
    "Cape Verde": "Cabo Verde",
    "Colombia": "Colombia",
    "Croatia": "Croacia",
    "Curacao": "Curazao",
    "Ecuador": "Ecuador",
    "Egypt": "Egipto",
    "England": "Inglaterra",
    "France": "Francia",
    "Germany": "Alemania",
    "Ghana": "Ghana",
    "Haiti": "Haití",
    "Iran": "Irán",
    "Ivory Coast": "Costa de Marfil",
    "Japan": "Japón",
    "Mexico": "México",
    "Morocco": "Marruecos",
    "Netherlands": "Países Bajos",
    "New Zealand": "Nueva Zelanda",
    "Norway": "Noruega",
    "Paraguay": "Paraguay",
    "Portugal": "Portugal",
    "Qatar": "Qatar",
    "Saudi Arabia": "Arabia Saudí",
    "Scotland": "Escocia",
    "Senegal": "Senegal",
    "South Africa": "Sudáfrica",
    "Spain": "España",
    "Sweden": "Suecia",
    "Switzerland": "Suiza",
    "Tunisia": "Túnez",
    "Turkey": "Turquía",
    "United States": "Estados Unidos",
    "Uruguay": "Uruguay"
}

def norm(text):
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower().replace("&", " y ")
    text = re.sub(r"[^a-z0-9\s/-]", " ", text)
    text = text.replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()

def canon_team(value):
    nv = norm(value)
    for canonical, variants in TEAM_VARIANTS.items():
        if nv == norm(canonical) or nv in [norm(v) for v in variants]:
            return canonical
    return value.strip() if value else ""

def pair_key(team1, team2):
    return tuple(sorted([norm(canon_team(team1)), norm(canon_team(team2))]))

def item_key(item):
    return pair_key(item.get("team1"), item.get("team2"))

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Mundial2026Tracker/1.3.5"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")

def fetch_json(url):
    return json.loads(fetch(url))

def abs_url(href):
    if href.startswith("http"):
        return href
    return "https://www.rtve.es" + href

def clean_text(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()

def has_team(text, team):
    nt = norm(text)
    for variant in TEAM_VARIANTS.get(canon_team(team), [team]):
        v = norm(variant)
        if re.search(rf"(^|\s){re.escape(v)}($|\s)", nt):
            return True
    return False

def extract_links_from_html(html):
    links = []
    for match in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
        href, body = match.groups()
        low = href.lower()
        if "rtve.es" not in low and not low.startswith("/"):
            continue
        if not ("/play/videos/" in low or "/deportes/" in low or "/play/" in low):
            continue

        start = max(0, match.start() - 900)
        end = min(len(html), match.end() + 900)
        context = clean_text(html[start:end])
        title = clean_text(body)
        if len(title) < 10:
            slug = href.strip("/").split("/")[-2] if "/" in href.strip("/") else href
            title = slug.replace("-", " ")
        links.append({"href": abs_url(href), "title": title[:240], "context": context[:700]})
    return links

def score_link(link, team1, team2):
    text = " ".join([link["href"], link["title"], link["context"]])
    ntext = norm(text)
    if not (has_team(text, team1) and has_team(text, team2)):
        return 0

    score = 10
    if "resumen" in ntext: score += 25
    if "goles" in ntext: score += 15
    if "mejores jugadas" in ntext: score += 15
    if "mundial" in ntext: score += 10
    if "fifa" in ntext: score += 5
    if "/play/videos/" in link["href"]: score += 10
    if "/directo/" in link["href"]: score -= 20
    if "directo" in ntext and "resumen" not in ntext: score -= 20
    if "programa" in ntext and "resumen" not in ntext: score -= 10
    return score

def best_video_from_html(html, team1, team2):
    candidates = []
    for link in extract_links_from_html(html):
        s = score_link(link, team1, team2)
        if s >= 25:
            candidates.append((s, link))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    link = candidates[0][1]
    return {
        "team1": canon_team(team1),
        "team2": canon_team(team2),
        "title": link["title"],
        "url": link["href"],
        "source": "RTVE Play"
    }

def search_rtve_for_match(team1, team2):
    t1_es = TEAM_ES.get(canon_team(team1), team1)
    t2_es = TEAM_ES.get(canon_team(team2), team2)
    queries = [
        f'{t1_es} {t2_es} resumen Mundial 2026',
        f'{t2_es} {t1_es} resumen Mundial 2026',
        f'{team1} {team2} highlights World Cup 2026 RTVE',
        f'{t1_es} {t2_es} goles Mundial 2026 RTVE',
    ]
    for query in queries:
        url = SEARCH_URL + urllib.parse.quote_plus(query)
        try:
            html = fetch(url)
            result = best_video_from_html(html, team1, team2)
            if result:
                print(f"  encontrado por búsqueda: {team1} vs {team2} -> {result['url']}")
                return result
        except Exception as exc:
            print(f"  búsqueda fallida para {team1} vs {team2}: {exc}")
    return None

def load_played_matches():
    data = fetch_json(OPENFOOTBALL_URL)
    matches = []
    for m in data.get("matches", []):
        score = m.get("score", {})
        if isinstance(score, dict) and isinstance(score.get("ft"), list):
            team1 = canon_team(m.get("team1", ""))
            team2 = canon_team(m.get("team2", ""))
            if team1 and team2:
                matches.append({"team1": team1, "team2": team2, "num": m.get("num"), "date": m.get("date")})
    return matches

def extract_from_collection():
    html = fetch(COLLECTION_URL)
    videos = []
    # Broad scan: identify links that already contain two teams.
    for link in extract_links_from_html(html):
        text = " ".join([link["title"], link["href"], link["context"]])
        teams = []
        for canonical in TEAM_VARIANTS:
            if has_team(text, canonical):
                teams.append(canonical)
        if len(teams) >= 2 and score_link(link, teams[0], teams[1]) >= 25:
            videos.append({
                "team1": teams[0],
                "team2": teams[1],
                "title": link["title"],
                "url": link["href"],
                "source": "RTVE Play"
            })
    return videos

def main():
    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except Exception:
            previous = {}

    by_pair = {}
    for item in previous.get("videos", []):
        key = item_key(item)
        if key[0] and key[1]:
            by_pair[key] = item

    # 1. First pass: collection page.
    try:
        collection_videos = extract_from_collection()
        print(f"colección RTVE: {len(collection_videos)} candidatos")
        for item in collection_videos:
            by_pair[item_key(item)] = item
    except Exception as exc:
        print(f"colección RTVE no disponible o no parseable: {exc}")

    # 2. Stronger pass: search RTVE match by match for played fixtures missing a video.
    try:
        played = load_played_matches()
        print(f"partidos finalizados detectados en OpenFootball: {len(played)}")
    except Exception as exc:
        print(f"no se pudieron cargar partidos de OpenFootball: {exc}")
        played = []

    for match in played:
        key = pair_key(match["team1"], match["team2"])
        if key in by_pair:
            continue
        result = search_rtve_for_match(match["team1"], match["team2"])
        if result:
            by_pair[key] = result
        else:
            print(f"  no encontrado: {match['team1']} vs {match['team2']}")

    output = {
        "version": "1.5",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_collection": COLLECTION_URL,
        "videos": sorted(by_pair.values(), key=lambda x: (x.get("team1",""), x.get("team2","")))
    }

    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"videos-rtve.json actualizado: {len(output['videos'])} vídeos")
    for item in output["videos"]:
        print(f"- {item['team1']} vs {item['team2']}")

if __name__ == "__main__":
    main()
