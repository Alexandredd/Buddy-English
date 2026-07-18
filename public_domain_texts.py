"""Textos em ingles de dominio publico para treino de leitura e pronuncia."""

from typing import Dict, List
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import requests


PublicText = Dict[str, str]


PUBLIC_DOMAIN_TEXTS: List[PublicText] = [
    {
        "title": "Pride and Prejudice - Opening",
        "author": "Jane Austen",
        "year": "1813",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "It is a truth universally acknowledged, that a single man in possession of a good fortune, "
            "must be in want of a wife.\n\n"
            "However little known the feelings or views of such a man may be on his first entering a neighbourhood, "
            "this truth is so well fixed in the minds of the surrounding families, that he is considered as the "
            "rightful property of some one or other of their daughters."
        ),
    },
    {
        "title": "A Tale of Two Cities - Opening",
        "author": "Charles Dickens",
        "year": "1859",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, "
            "it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, "
            "it was the spring of hope, it was the winter of despair.\n\n"
            "We had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct "
            "the other way."
        ),
    },
    {
        "title": "Sherlock Holmes - A Scandal in Bohemia",
        "author": "Arthur Conan Doyle",
        "year": "1891",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name.\n\n"
            "In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. "
            "All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind."
        ),
    },
]


DAILY_PUBLIC_TEXT_POOL: List[PublicText] = [
    {
        "title": "Moby-Dick - Opening",
        "author": "Herman Melville",
        "year": "1851",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "Call me Ishmael. Some years ago - never mind how long precisely - having little or no money in my purse, "
            "and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part "
            "of the world."
        ),
    },
    {
        "title": "The Adventures of Tom Sawyer - Opening",
        "author": "Mark Twain",
        "year": "1876",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "\"Tom!\" No answer. \"Tom!\" No answer. \"What's gone with that boy, I wonder? You TOM!\"\n\n"
            "No answer. The old lady pulled her spectacles down and looked over them about the room; then she put them "
            "up and looked out under them."
        ),
    },
    {
        "title": "Jane Eyre - Opening",
        "author": "Charlotte Bronte",
        "year": "1847",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "There was no possibility of taking a walk that day. We had been wandering, indeed, in the leafless shrubbery "
            "an hour in the morning; but since dinner the cold winter wind had brought with it clouds so sombre and a rain "
            "so penetrating, that further out-door exercise was now out of the question."
        ),
    },
    {
        "title": "The Time Machine - Opening",
        "author": "H. G. Wells",
        "year": "1895",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "The Time Traveller (for so it will be convenient to speak of him) was expounding a recondite matter to us. "
            "His grey eyes shone and twinkled, and his usually pale face was flushed and animated."
        ),
    },
    {
        "title": "Frankenstein - Opening",
        "author": "Mary Shelley",
        "year": "1818",
        "source": "Project Gutenberg (Public Domain)",
        "text": (
            "You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have "
            "regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister "
            "of my welfare."
        ),
    },
]


EXTRA_PUBLIC_TEXTS_FILE = Path(__file__).with_name("public_domain_texts_extra.json")
PUBLIC_TEXTS_META_FILE = Path(__file__).with_name("public_domain_texts_meta.json")


def _text_id(item: PublicText) -> str:
    return str(item.get("title", "")).strip().lower()


def load_extra_public_texts() -> List[PublicText]:
    if not EXTRA_PUBLIC_TEXTS_FILE.exists():
        return []
    try:
        with EXTRA_PUBLIC_TEXTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    valid: List[PublicText] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if all(key in item for key in ["title", "author", "year", "source", "text"]):
            valid.append(
                {
                    "title": str(item["title"]),
                    "author": str(item["author"]),
                    "year": str(item["year"]),
                    "source": str(item["source"]),
                    "text": str(item["text"]),
                }
            )
    return valid


def _save_extra_public_texts(items: List[PublicText]) -> None:
    with EXTRA_PUBLIC_TEXTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)


def add_extra_public_text(item: PublicText) -> bool:
    extras = load_extra_public_texts()
    existing = {_text_id(text) for text in PUBLIC_DOMAIN_TEXTS + extras}
    if _text_id(item) in existing:
        return False

    extras.append(item)
    _save_extra_public_texts(extras)
    return True


def _load_public_texts_meta() -> Dict[str, str]:
    if not PUBLIC_TEXTS_META_FILE.exists():
        return {}
    try:
        with PUBLIC_TEXTS_META_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        return {}
    return {}


def get_last_auto_update_date() -> str:
    return _load_public_texts_meta().get("last_auto_update_date", "")


def set_last_auto_update_date(date_iso: str) -> None:
    meta = _load_public_texts_meta()
    payload = {
        **meta,
        "last_auto_update_date": str(date_iso),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with PUBLIC_TEXTS_META_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def get_last_online_fetch_status() -> Dict[str, str]:
    meta = _load_public_texts_meta()
    return {
        "updated_at": str(meta.get("online_fetch_updated_at", "")),
        "status": str(meta.get("online_fetch_status", "")),
        "details": str(meta.get("online_fetch_details", "")),
    }


def _set_last_online_fetch_status(status: str, details: str = "") -> None:
    meta = _load_public_texts_meta()
    payload = {
        **meta,
        "online_fetch_updated_at": datetime.now(timezone.utc).isoformat(),
        "online_fetch_status": str(status),
        "online_fetch_details": str(details),
    }
    with PUBLIC_TEXTS_META_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _extract_excerpt(raw_text: str, max_chars: int = 900) -> str:
    text = (raw_text or "").strip()
    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Remove header markers commonly present in Gutenberg plain text.
    start_marker = "*** START OF"
    if start_marker in text:
        _, _, remainder = text.partition(start_marker)
        if "***" in remainder:
            _, _, text = remainder.partition("***")
            text = text.strip()

    if len(text) <= max_chars:
        return text

    cut = text[:max_chars]
    last_space = cut.rfind(" ")
    if last_space > 0:
        cut = cut[:last_space]
    return cut.strip() + "..."


def _fetch_gutendex_candidates(limit: int = 1) -> List[PublicText]:
    desired = max(1, limit)
    candidates: List[PublicText] = []

    try:
        response = requests.get(
            "https://gutendex.com/books",
            params={
                "languages": "en",
                "copyright": "false",
                "sort": "popular",
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return []

    results = payload.get("results", []) if isinstance(payload, dict) else []
    if not isinstance(results, list):
        return []

    for book in results:
        if len(candidates) >= desired * 3:
            break
        if not isinstance(book, dict):
            continue

        title = str(book.get("title", "")).strip()
        if not title:
            continue

        authors = book.get("authors", [])
        author_name = "Unknown"
        if isinstance(authors, list) and authors:
            first_author = authors[0] if isinstance(authors[0], dict) else {}
            author_name = str(first_author.get("name", "Unknown")).strip() or "Unknown"

        summary_text = ""
        summaries = book.get("summaries", [])
        if isinstance(summaries, list) and summaries:
            summary_text = str(summaries[0]).strip()

        excerpt = _extract_excerpt(summary_text)
        if not excerpt:
            formats = book.get("formats", {})
            plain_url = ""
            if isinstance(formats, dict):
                for key, value in formats.items():
                    k = str(key).lower()
                    if "text/plain" in k and isinstance(value, str) and value.startswith("http"):
                        plain_url = value
                        break
            if plain_url:
                try:
                    text_resp = requests.get(plain_url, timeout=15)
                    text_resp.raise_for_status()
                    excerpt = _extract_excerpt(text_resp.text)
                except requests.RequestException:
                    excerpt = ""

        if not excerpt:
            continue

        candidates.append(
            {
                "title": f"{title} - Excerpt",
                "author": author_name,
                "year": "-",
                "source": "Gutendex / Project Gutenberg (Public Domain)",
                "text": excerpt,
            }
        )

    return candidates[: desired * 2]


def fetch_and_incorporate_online_public_texts(limit: int = 1) -> int:
    added = 0
    candidates = _fetch_gutendex_candidates(limit=max(1, limit))
    if not candidates:
        _set_last_online_fetch_status(
            "no_candidates",
            "Nenhum candidato online disponível (rede, API ou conteúdo sem trecho válido).",
        )
        return 0

    duplicate_count = 0
    for candidate in candidates:
        if added >= max(1, limit):
            break
        if add_extra_public_text(candidate):
            added += 1
        else:
            duplicate_count += 1

    if added > 0:
        _set_last_online_fetch_status(
            "ok",
            f"Incorporados {added} texto(s) online.",
        )
    elif duplicate_count > 0:
        _set_last_online_fetch_status(
            "duplicates_only",
            "A busca retornou textos já existentes (sem novos para adicionar).",
        )
    else:
        _set_last_online_fetch_status(
            "no_new_items",
            "A busca online ocorreu, mas não gerou novos textos válidos.",
        )
    return added


def incorporate_daily_public_texts(limit: int = 1, include_online: bool = True) -> int:
    desired = max(1, limit)
    added = 0
    for candidate in DAILY_PUBLIC_TEXT_POOL:
        if added >= desired:
            break
        if add_extra_public_text(candidate):
            added += 1

    remaining = desired - added
    if include_online and remaining > 0:
        added += fetch_and_incorporate_online_public_texts(limit=remaining)

    return added


def get_all_public_texts() -> List[PublicText]:
    return PUBLIC_DOMAIN_TEXTS + load_extra_public_texts()


def list_public_texts() -> List[PublicText]:
    """Retorna todos os textos publicos disponiveis."""
    return get_all_public_texts()


def list_public_titles() -> List[str]:
    """Retorna os titulos dos textos publicos."""
    return [item["title"] for item in get_all_public_texts()]


def get_public_text_by_title(title: str) -> PublicText:
    """Busca um texto publico por titulo."""
    all_texts = get_all_public_texts()
    for item in all_texts:
        if item["title"] == title:
            return item
    return all_texts[0]


def split_paragraphs(text: str) -> List[str]:
    """Separa o texto em paragrafos nao vazios."""
    return [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
