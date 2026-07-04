#!/usr/bin/env python3
import json
import re
import unicodedata
import urllib.request
from html import unescape
from pathlib import Path
from datetime import datetime, timezone

COLLECTION_URL = "https://www.rtve.es/play/colecciones/mundial-2026-resumenes/4735/"
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
    "Japan": ["japan", "japon", "japón"],
    "Mexico": ["mexico", "méxico"],
    "Morocco": ["morocco", "marruecos"],
    "Netherlands": ["netherlands", "paises bajos", "países bajos"],
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

def norm(text):
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower().replace("&", " y ")
    text = re.sub(r"[^a-z0-9\s/-]", " ", text)
    text = text.replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Mundial2026Tracker/1.3.3"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")

def abs_url(href):
    return href if href.startswith("http") else "https://www.rtve.es" + href

def clean_title(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()

def find_teams(text):
    ntext = norm(text)
    hits = []
    for canonical, variants in TEAM_VARIANTS.items():
        best = None
        for variant in variants:
            v = norm(variant)
            m = re.search(rf"(^|\s){re.escape(v)}($|\s)", ntext)
            if m:
                best = m.start() if best is None else min(best, m.start())
        if best is not None:
            hits.append((best, canonical))
    hits.sort()
    out = []
    for _, team in hits:
        if team not in out:
            out.append(team)
    return out

def extract_links(html):
    links = []
    for match in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
        href, body = match.groups()
        low = href.lower()
        if "rtve.es" not in low and not low.startswith("/play/"):
            continue
        if "/play/videos/" not in low:
            continue
        combined = norm(href + " " + body)
        if not any(x in combined for x in ["mundial", "fifa", "resumen", "goles"]):
            continue
        start = max(0, match.start() - 900)
        end = min(len(html), match.end() + 900)
        context = clean_title(html[start:end])
        title = clean_title(body)
        if len(title) < 12:
            slug = href.strip("/").split("/")[-2] if "/" in href.strip("/") else href
            title = slug.replace("-", " ")
        links.append({"href": abs_url(href), "title": title[:240], "context": context[:500]})
    return links

def extract_videos(html):
    candidates = []
    for item in extract_links(html):
        text = " ".join([item["title"], item["href"], item["context"]])
        teams = find_teams(text)
        if len(teams) < 2:
            continue
        ntext = norm(text)
        if not any(x in ntext for x in ["resumen", "goles", "mejores jugadas"]):
            continue
        candidates.append({
            "team1": teams[0],
            "team2": teams[1],
            "title": item["title"],
            "url": item["href"],
            "source": "RTVE Play"
        })

    seen = set()
    videos = []
    for item in candidates:
        key = tuple(sorted([norm(item["team1"]), norm(item["team2"])]))
        if key not in seen:
            seen.add(key)
            videos.append(item)
    return videos

def pair_key(item):
    return tuple(sorted([norm(item.get("team1")), norm(item.get("team2"))]))

def main():
    html = fetch(COLLECTION_URL)
    videos = extract_videos(html)

    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except Exception:
            previous = {}

    by_pair = {}
    for item in previous.get("videos", []) + videos:
        key = pair_key(item)
        if key[0] and key[1]:
            by_pair[key] = item

    output = {
        "version": "1.3",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_collection": COLLECTION_URL,
        "videos": sorted(by_pair.values(), key=lambda x: (x.get("team1",""), x.get("team2","")))
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"videos-rtve.json actualizado: {len(output['videos'])} vídeos")
    for item in sorted(videos, key=lambda x: (x.get("team1",""), x.get("team2",""))):
        print(f"- {item['team1']} vs {item['team2']}")

if __name__ == "__main__":
    main()
