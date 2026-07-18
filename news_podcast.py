"""Busca manchetes atuais do mundo em ingles para o modulo de podcast de noticias."""

from pathlib import Path
import json
import re
import html
from typing import List, Dict
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree

import requests


NewsItem = Dict[str, str]

CACHE_FILE = Path(__file__).with_name("news_podcast_cache.json")

RSS_FEEDS = [
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "NPR World", "url": "https://feeds.npr.org/1004/rss.xml"},
]


def _strip_html(texto: str) -> str:
    """Remove tags HTML e normaliza espacos de um trecho de texto."""
    limpo = re.sub(r"<[^>]+>", " ", texto or "")
    limpo = html.unescape(limpo)
    return re.sub(r"\s+", " ", limpo).strip()


def _parse_rss(xml_text: str, source_name: str) -> List[NewsItem]:
    itens: List[NewsItem] = []
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        return itens

    for item in root.findall(".//item"):
        titulo = _strip_html(item.findtext("title", ""))
        resumo = _strip_html(item.findtext("description", ""))
        link = (item.findtext("link", "") or "").strip()
        publicado = (item.findtext("pubDate", "") or "").strip()
        if not titulo:
            continue
        itens.append(
            {
                "title": titulo,
                "summary": resumo,
                "link": link,
                "published": publicado,
                "source": source_name,
            }
        )
    return itens


def _fetch_from_feeds(limit: int) -> List[NewsItem]:
    coletados: List[NewsItem] = []
    for feed in RSS_FEEDS:
        if len(coletados) >= limit:
            break
        try:
            response = requests.get(feed["url"], timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            continue
        coletados.extend(_parse_rss(response.text, feed["name"]))

    vistos = set()
    unicos: List[NewsItem] = []
    for entrada in coletados:
        chave = entrada["title"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(entrada)

    return unicos[:limit]


def _load_cache() -> Dict[str, object]:
    if not CACHE_FILE.exists():
        return {}
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        return {}
    return {}


def _save_cache(items: List[NewsItem]) -> None:
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }
    with CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _is_cache_fresh(updated_at_iso: str, minutes: int = 60) -> bool:
    try:
        updated_at = datetime.fromisoformat(updated_at_iso)
    except ValueError:
        return False
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - updated_at < timedelta(minutes=minutes)


def get_world_news(limit: int = 5, force_refresh: bool = False) -> List[NewsItem]:
    """Retorna manchetes atuais do mundo, com cache local para reduzir chamadas externas."""
    limit = max(1, min(limit, 10))
    cache = _load_cache()
    cached_items = cache.get("items", []) if isinstance(cache, dict) else []
    updated_at = cache.get("updated_at", "") if isinstance(cache, dict) else ""

    if (
        not force_refresh
        and isinstance(cached_items, list)
        and cached_items
        and isinstance(updated_at, str)
        and _is_cache_fresh(updated_at)
    ):
        return cached_items[:limit]

    fetched = _fetch_from_feeds(limit=max(limit, 8))
    if fetched:
        _save_cache(fetched)
        return fetched[:limit]

    if isinstance(cached_items, list) and cached_items:
        return cached_items[:limit]

    return []


def get_cache_info() -> Dict[str, str]:
    """Retorna metadados simples do cache para exibicao na interface."""
    cache = _load_cache()
    updated_at = cache.get("updated_at", "") if isinstance(cache, dict) else ""
    items = cache.get("items", []) if isinstance(cache, dict) else []
    return {"updated_at": updated_at, "count": str(len(items) if isinstance(items, list) else 0)}


def build_episode_script(items: List[NewsItem]) -> str:
    """Monta o roteiro em ingles do episodio a partir das manchetes coletadas."""
    partes = []
    for indice, item in enumerate(items, start=1):
        titulo = (item.get("title") or "").strip()
        resumo = (item.get("summary") or "").strip()
        segmento = f"Story {indice}. {titulo}."
        if resumo and resumo.casefold() != titulo.casefold():
            segmento += f" {resumo}"
        partes.append(segmento)
    return "\n\n".join(partes)
