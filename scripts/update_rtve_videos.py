#!/usr/bin/env python3
import json, re, unicodedata, urllib.request
from html import unescape
from pathlib import Path
from datetime import datetime, timezone
COLLECTION_URL='https://www.rtve.es/play/colecciones/mundial-2026-resumenes/4735/'
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'videos-rtve.json'
ALIASES={'mexico':'Mexico','sudafrica':'South Africa','canada':'Canada','bosnia':'Bosnia and Herzegovina','brasil':'Brazil','marruecos':'Morocco','alemania':'Germany','curazao':'Curacao','espana':'Spain','cabo verde':'Cape Verde','francia':'France','senegal':'Senegal','inglaterra':'England','croacia':'Croatia','suiza':'Switzerland','eeuu':'United States','estados unidos':'United States','australia':'Australia','paises bajos':'Netherlands','suecia':'Sweden','arabia saudi':'Saudi Arabia','argentina':'Argentina','austria':'Austria','ghana':'Ghana','escocia':'Scotland','ecuador':'Ecuador','uruguay':'Uruguay','colombia':'Colombia','portugal':'Portugal'}
def norm(t):
    t=unescape(t or ''); t=re.sub(r'<[^>]+>',' ',t); t=unicodedata.normalize('NFD',t); t=''.join(ch for ch in t if unicodedata.category(ch)!='Mn'); t=t.lower(); t=t.replace('&',' y '); t=re.sub(r'[^\w\s-]',' ',t); t=t.replace('-',' '); return re.sub(r'\s+',' ',t).strip()
def canon(team): return ALIASES.get(norm(team), team.strip())
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Mundial2026Tracker/1.0'});
    with urllib.request.urlopen(req,timeout=30) as r: return r.read().decode('utf-8',errors='replace')
def abs_url(h): return h if h.startswith('http') else 'https://www.rtve.es'+h
def extract(html):
    out=[]
    for m in re.finditer(r'<a[^>]+href="([^"]*resumen-partido-mundial-2026/[^"]*)"[^>]*>(.*?)</a>', html, re.I|re.S):
        href, body=m.groups(); title=re.sub(r'<[^>]+>',' ',body); title=re.sub(r'\s+',' ',unescape(title)).strip()
        if len(title)<12:
            ctx=html[max(0,m.start()-500):min(len(html),m.end()+500)]; title=re.sub(r'<[^>]+>',' ',ctx); title=re.sub(r'\s+',' ',unescape(title)).strip()[:220]
        tm=re.search(r'([A-Za-zÁÉÍÓÚÜÑáéíóúüñ .]+?)\s*-\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ .]+?)\s*:', title)
        if not tm: continue
        out.append({'team1':canon(tm.group(1)),'team2':canon(tm.group(2)),'title':title,'url':abs_url(href),'source':'RTVE Play'})
    seen={};
    for item in out:
        key=tuple(sorted([norm(item['team1']),norm(item['team2'])])); seen[key]=item
    return list(seen.values())
def main():
    html=fetch(COLLECTION_URL); videos=extract(html)
    prev={}
    if OUTPUT.exists():
        try: prev=json.loads(OUTPUT.read_text(encoding='utf-8'))
        except Exception: prev={}
    merged={}
    for item in prev.get('videos',[])+videos:
        key=tuple(sorted([norm(item.get('team1')),norm(item.get('team2'))]));
        if key[0] and key[1]: merged[key]=item
    data={'version':'1.1','updated_at':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'source_collection':COLLECTION_URL,'videos':sorted(merged.values(),key=lambda x:(x.get('team1',''),x.get('team2','')))}
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"videos-rtve.json actualizado: {len(data['videos'])} vídeos")
if __name__=='__main__': main()
