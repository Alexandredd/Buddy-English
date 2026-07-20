"""Frases comuns do inglês americano organizadas por contexto."""

from pathlib import Path
import json
import random
import csv
from io import StringIO
from typing import List, Dict
import requests
from datetime import datetime, timedelta, timezone


Phrase = Dict[str, str]


PHRASES: List[Phrase] = [
    {
        "context": "Saudações",
        "english": "How's it going?",
        "when_to_use": "Forma informal para cumprimentar amigos, colegas ou pessoas da mesma faixa etária.",
        "best_translation": "Como vão as coisas?",
    },
    {
        "context": "Saudações",
        "english": "Nice to meet you.",
        "when_to_use": "Quando conhece alguém pela primeira vez em situações formais ou neutras.",
        "best_translation": "Prazer em conhecer você.",
    },
    {
        "context": "Restaurante",
        "english": "Can I see the menu, please?",
        "when_to_use": "Ao pedir o cardápio para o garçom em restaurantes ou cafeterias.",
        "best_translation": "Posso ver o cardápio, por favor?",
    },
    {
        "context": "Restaurante",
        "english": "Could I get the check, please?",
        "when_to_use": "Para pedir a conta no fim da refeição. Em inglês americano usa-se check.",
        "best_translation": "Pode me trazer a conta, por favor?",
    },
    {
        "context": "Trabalho",
        "english": "I'm running a bit late.",
        "when_to_use": "Quando vai se atrasar para uma reunião, aula ou compromisso.",
        "best_translation": "Vou me atrasar um pouco.",
    },
    {
        "context": "Trabalho",
        "english": "Let's touch base tomorrow.",
        "when_to_use": "Expressão comum em ambiente profissional para combinar alinhamento posterior.",
        "best_translation": "Vamos nos alinhar amanhã.",
    },
    {
        "context": "Compras",
        "english": "Do you have this in a different size?",
        "when_to_use": "Ao pedir outro tamanho de roupa, calçado ou acessório em lojas.",
        "best_translation": "Você tem isso em outro tamanho?",
    },
    {
        "context": "Compras",
        "english": "I'm just looking, thanks.",
        "when_to_use": "Quando o vendedor oferece ajuda e você ainda está apenas olhando.",
        "best_translation": "Estou só dando uma olhada, obrigado(a).",
    },
    {
        "context": "Transporte",
        "english": "How much is the fare?",
        "when_to_use": "Ao perguntar o preço da passagem em transporte público ou táxi.",
        "best_translation": "Quanto custa a passagem?",
    },
    {
        "context": "Transporte",
        "english": "Could you drop me off here?",
        "when_to_use": "Para pedir ao motorista de táxi ou aplicativo que pare naquele ponto.",
        "best_translation": "Você pode me deixar aqui?",
    },
    {
        "context": "Social",
        "english": "I'm in!",
        "when_to_use": "Quando aceita um convite de forma animada e informal.",
        "best_translation": "Topo!",
    },
    {
        "context": "Social",
        "english": "Maybe next time.",
        "when_to_use": "Para recusar convites com educação sem parecer rude.",
        "best_translation": "Quem sabe na próxima.",
    },
    {
        "context": "Emergência",
        "english": "I need help.",
        "when_to_use": "Situações urgentes em que você precisa de apoio imediato.",
        "best_translation": "Eu preciso de ajuda.",
    },
    {
        "context": "Emergência",
        "english": "Please call 911.",
        "when_to_use": "Em emergências médicas ou de segurança nos EUA.",
        "best_translation": "Por favor, ligue para o 911.",
    },
]

SUGGESTION_POOL: Dict[str, List[Phrase]] = {
    "Saudações": [
        {
            "context": "Saudações",
            "english": "What's up?",
            "when_to_use": "Cumprimento informal entre amigos.",
            "best_translation": "E aí?",
        },
        {
            "context": "Saudações",
            "english": "Long time no see.",
            "when_to_use": "Quando reencontra alguém depois de muito tempo.",
            "best_translation": "Quanto tempo!",
        },
        {
            "context": "Saudações",
            "english": "How have you been?",
            "when_to_use": "Perguntar como a pessoa está em tom amistoso.",
            "best_translation": "Como você tem estado?",
        },
    ],
    "Restaurante": [
        {
            "context": "Restaurante",
            "english": "Could we have some water, please?",
            "when_to_use": "Para pedir agua durante a refeicao.",
            "best_translation": "Podemos pedir agua, por favor?",
        },
        {
            "context": "Restaurante",
            "english": "I'd like to order now.",
            "when_to_use": "Quando estiver pronto para fazer o pedido.",
            "best_translation": "Gostaria de pedir agora.",
        },
        {
            "context": "Restaurante",
            "english": "Can I get this to go?",
            "when_to_use": "Para pedir a refeicao para viagem.",
            "best_translation": "Posso pedir isso para viagem?",
        },
    ],
    "Trabalho": [
        {
            "context": "Trabalho",
            "english": "I'll get back to you by noon.",
            "when_to_use": "Para confirmar retorno com prazo no ambiente profissional.",
            "best_translation": "Te dou retorno ate o meio-dia.",
        },
        {
            "context": "Trabalho",
            "english": "Can we move this meeting?",
            "when_to_use": "Quando precisa remarcar uma reuniao.",
            "best_translation": "Podemos remarcar esta reuniao?",
        },
        {
            "context": "Trabalho",
            "english": "I'm on it.",
            "when_to_use": "Resposta curta para dizer que vai cuidar da tarefa.",
            "best_translation": "Estou cuidando disso.",
        },
    ],
    "Compras": [
        {
            "context": "Compras",
            "english": "Can I try this on?",
            "when_to_use": "Perguntar se pode experimentar uma peca de roupa.",
            "best_translation": "Posso experimentar isso?",
        },
        {
            "context": "Compras",
            "english": "Is this on sale?",
            "when_to_use": "Perguntar se o item esta em promocao.",
            "best_translation": "Isso esta em promocao?",
        },
        {
            "context": "Compras",
            "english": "Do you take credit cards?",
            "when_to_use": "Confirmar forma de pagamento.",
            "best_translation": "Vocês aceitam cartao de credito?",
        },
    ],
    "Transporte": [
        {
            "context": "Transporte",
            "english": "Which line goes downtown?",
            "when_to_use": "Para saber qual linha vai para o centro.",
            "best_translation": "Qual linha vai para o centro?",
        },
        {
            "context": "Transporte",
            "english": "Is this seat taken?",
            "when_to_use": "Perguntar se um assento esta ocupado.",
            "best_translation": "Este assento esta ocupado?",
        },
        {
            "context": "Transporte",
            "english": "What time is the next bus?",
            "when_to_use": "Perguntar o horario do proximo onibus.",
            "best_translation": "Que horas passa o proximo onibus?",
        },
    ],
    "Social": [
        {
            "context": "Social",
            "english": "That sounds great.",
            "when_to_use": "Para demonstrar entusiasmo com uma ideia ou convite.",
            "best_translation": "Parece otimo.",
        },
        {
            "context": "Social",
            "english": "I'm down for that.",
            "when_to_use": "Aceitar convite de modo informal.",
            "best_translation": "Eu topo isso.",
        },
        {
            "context": "Social",
            "english": "Let's catch up soon.",
            "when_to_use": "Para combinar de conversar ou encontrar em breve.",
            "best_translation": "Vamos nos atualizar em breve.",
        },
    ],
    "Emergência": [
        {
            "context": "Emergência",
            "english": "I need a doctor.",
            "when_to_use": "Quando precisa de atendimento medico urgente.",
            "best_translation": "Eu preciso de um medico.",
        },
        {
            "context": "Emergência",
            "english": "Where is the nearest hospital?",
            "when_to_use": "Para localizar atendimento de emergencia.",
            "best_translation": "Onde fica o hospital mais proximo?",
        },
        {
            "context": "Emergência",
            "english": "Please stay with me.",
            "when_to_use": "Pedido de apoio em situacao de emergencia.",
            "best_translation": "Por favor, fique comigo.",
        },
    ],
}

EXTRA_PHRASES_FILE = Path(__file__).with_name("daily_phrases_extra.json")
ONLINE_CACHE_FILE = Path(__file__).with_name("daily_phrases_online_cache.json")
AUTO_UPDATE_META_FILE = Path(__file__).with_name("daily_phrases_meta.json")


def _phrase_id(phrase: Phrase) -> str:
    return f"{phrase['context']}::{phrase['english']}".strip().lower()


def load_extra_phrases() -> List[Phrase]:
    """Carrega frases extras persistidas em arquivo local."""
    if not EXTRA_PHRASES_FILE.exists():
        return []
    try:
        with EXTRA_PHRASES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    valid_phrases: List[Phrase] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if all(key in item for key in ("context", "english", "when_to_use", "best_translation")):
            valid_phrases.append(
                {
                    "context": str(item["context"]),
                    "english": str(item["english"]),
                    "when_to_use": str(item["when_to_use"]),
                    "best_translation": str(item["best_translation"]),
                }
            )
    return valid_phrases


def save_extra_phrase(phrase: Phrase) -> bool:
    """Salva uma frase extra no arquivo local, sem duplicar entradas."""
    extras = load_extra_phrases()
    existing_ids = {_phrase_id(item) for item in PHRASES + extras}
    if _phrase_id(phrase) in existing_ids:
        return False

    extras.append(phrase)
    with EXTRA_PHRASES_FILE.open("w", encoding="utf-8") as file:
        json.dump(extras, file, ensure_ascii=False, indent=2)
    return True


def save_extra_phrases_bulk(phrases: List[Phrase]) -> Dict[str, int]:
    """Salva varias frases extras, ignorando duplicadas e invalidas."""
    extras = load_extra_phrases()
    existing_ids = {_phrase_id(item) for item in PHRASES + extras}
    added_count = 0
    duplicate_count = 0
    invalid_count = 0

    for phrase in phrases:
        if not isinstance(phrase, dict):
            invalid_count += 1
            continue

        if not all(key in phrase for key in ("context", "english", "when_to_use", "best_translation")):
            invalid_count += 1
            continue

        normalized = {
            "context": str(phrase["context"]).strip(),
            "english": str(phrase["english"]).strip(),
            "when_to_use": str(phrase["when_to_use"]).strip(),
            "best_translation": str(phrase["best_translation"]).strip(),
        }

        if not all(normalized.values()):
            invalid_count += 1
            continue

        phrase_id = _phrase_id(normalized)
        if phrase_id in existing_ids:
            duplicate_count += 1
            continue

        extras.append(normalized)
        existing_ids.add(phrase_id)
        added_count += 1

    if added_count:
        with EXTRA_PHRASES_FILE.open("w", encoding="utf-8") as file:
            json.dump(extras, file, ensure_ascii=False, indent=2)

    return {
        "added": added_count,
        "duplicates": duplicate_count,
        "invalid": invalid_count,
    }


def parse_phrases_json(content: str) -> List[Phrase]:
    """Converte texto JSON em lista de frases validaveis."""
    data = json.loads(content)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def parse_phrases_csv(content: str) -> List[Phrase]:
    """Converte texto CSV em lista de frases com colunas esperadas."""
    reader = csv.DictReader(StringIO(content))
    phrases: List[Phrase] = []
    for row in reader:
        if not row:
            continue
        phrases.append(
            {
                "context": (row.get("context") or "").strip(),
                "english": (row.get("english") or "").strip(),
                "when_to_use": (row.get("when_to_use") or "").strip(),
                "best_translation": (row.get("best_translation") or "").strip(),
            }
        )
    return phrases


def export_all_phrases_json() -> str:
    """Exporta todas as frases em JSON."""
    return json.dumps(get_all_phrases(), ensure_ascii=False, indent=2)


def export_all_phrases_csv() -> str:
    """Exporta todas as frases em CSV."""
    output = StringIO()
    fieldnames = ["context", "english", "when_to_use", "best_translation"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for phrase in get_all_phrases():
        writer.writerow({field: phrase.get(field, "") for field in fieldnames})
    return output.getvalue()


def _load_online_cache() -> Dict[str, object]:
    """Carrega o cache local das frases online."""
    if not ONLINE_CACHE_FILE.exists():
        return {}
    try:
        with ONLINE_CACHE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        return {}
    return {}


def _load_auto_update_meta() -> Dict[str, str]:
    """Carrega metadados da atualizacao automatica diaria."""
    if not AUTO_UPDATE_META_FILE.exists():
        return {}
    try:
        with AUTO_UPDATE_META_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        return {}
    return {}


def get_last_auto_update_date() -> str:
    """Retorna a data UTC (YYYY-MM-DD) da ultima auto-incorporacao."""
    return _load_auto_update_meta().get("last_auto_update_date", "")


def set_last_auto_update_date(date_iso: str) -> None:
    """Salva a data UTC (YYYY-MM-DD) da ultima auto-incorporacao."""
    payload = {"last_auto_update_date": date_iso}
    with AUTO_UPDATE_META_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _save_online_cache(phrases: List[Phrase]) -> None:
    """Salva frases online no cache local com timestamp UTC."""
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "phrases": phrases,
    }
    with ONLINE_CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _is_cache_fresh(updated_at_iso: str, hours: int = 24) -> bool:
    """Valida se o cache foi atualizado dentro da janela definida."""
    try:
        updated_at = datetime.fromisoformat(updated_at_iso)
    except ValueError:
        return False
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - updated_at < timedelta(hours=hours)


def _fetch_online_phrases_from_apis(limit: int = 3) -> List[Phrase]:
    """Busca frases em APIs publicas para enriquecer o modulo dinamicamente."""
    candidates: List[Phrase] = []

    # Advice Slip: frases curtas de conselhos em ingles.
    for _ in range(max(1, limit)):
        try:
            response = requests.get("https://api.adviceslip.com/advice", timeout=8)
            response.raise_for_status()
            data = response.json()
            advice_text = data.get("slip", {}).get("advice", "").strip()
            if advice_text:
                candidates.append(
                    {
                        "context": "Frases da internet",
                        "english": advice_text,
                        "when_to_use": "Em conversas informais para compartilhar um conselho curto.",
                        "best_translation": "",
                    }
                )
        except (requests.RequestException, ValueError):
            continue

    # ZenQuotes: frases de impacto e reflexao.
    while len(candidates) < max(1, limit):
        try:
            response = requests.get("https://zenquotes.io/api/random", timeout=8)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data:
                quote = (data[0].get("q") or "").strip()
                if quote:
                    candidates.append(
                        {
                            "context": "Frases da internet",
                            "english": quote,
                            "when_to_use": "Em conversas sociais para comentar uma ideia inspiradora.",
                            "best_translation": "",
                        }
                    )
        except (requests.RequestException, ValueError, AttributeError):
            break

    existing_ids = {_phrase_id(item) for item in get_all_phrases()}
    unique_candidates: List[Phrase] = []
    local_ids = set()
    for phrase in candidates:
        pid = _phrase_id(phrase)
        if pid in existing_ids or pid in local_ids:
            continue
        local_ids.add(pid)
        unique_candidates.append(phrase)

    random.shuffle(unique_candidates)
    return unique_candidates[: max(1, limit)]


def fetch_online_phrases(limit: int = 3, force_refresh: bool = False) -> List[Phrase]:
    """Retorna frases online com cache diario para reduzir chamadas externas."""
    cache = _load_online_cache()
    cached_phrases = cache.get("phrases", []) if isinstance(cache, dict) else []
    updated_at = cache.get("updated_at", "") if isinstance(cache, dict) else ""

    if (
        not force_refresh
        and isinstance(cached_phrases, list)
        and cached_phrases
        and isinstance(updated_at, str)
        and _is_cache_fresh(updated_at)
    ):
        existing_ids = {_phrase_id(item) for item in get_all_phrases()}
        available = [item for item in cached_phrases if _phrase_id(item) not in existing_ids]
        random.shuffle(available)
        return available[: max(1, limit)]

    fetched = _fetch_online_phrases_from_apis(limit=max(5, limit))
    if fetched:
        _save_online_cache(fetched)
    return fetched[: max(1, limit)]


def get_online_cache_info() -> Dict[str, str]:
    """Retorna metadados simples do cache para exibicao na interface."""
    cache = _load_online_cache()
    updated_at = cache.get("updated_at", "") if isinstance(cache, dict) else ""
    phrases = cache.get("phrases", []) if isinstance(cache, dict) else []

    if not isinstance(updated_at, str) or not updated_at:
        return {"status": "Sem cache", "updated_at": "-", "count": "0"}

    status = "Valido" if _is_cache_fresh(updated_at) else "Expirado"
    count = str(len(phrases)) if isinstance(phrases, list) else "0"
    return {"status": status, "updated_at": updated_at, "count": count}


def get_all_phrases() -> List[Phrase]:
    """Retorna base + frases extras salvas pelo usuario."""
    return PHRASES + load_extra_phrases()


def list_contexts() -> List[str]:
    """Retorna os contextos ordenados alfabeticamente."""
    return sorted({phrase["context"] for phrase in get_all_phrases()})


def filter_phrases(context: str) -> List[Phrase]:
    """Filtra frases por contexto."""
    phrases = get_all_phrases()
    if context == "Todos":
        return phrases
    return [phrase for phrase in phrases if phrase["context"] == context]


def suggest_new_phrases(context: str, limit: int = 3) -> List[Phrase]:
    """Sugere frases novas com base no contexto selecionado."""
    pool: List[Phrase] = []
    if context == "Todos":
        for suggestions in SUGGESTION_POOL.values():
            pool.extend(suggestions)
    else:
        pool = SUGGESTION_POOL.get(context, [])

    existing_ids = {_phrase_id(item) for item in get_all_phrases()}
    available = [item for item in pool if _phrase_id(item) not in existing_ids]

    if not available:
        return []

    random.shuffle(available)
    return available[: max(1, limit)]
