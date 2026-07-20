"""Módulo de chunks de aprendizado - Pedaços de conteúdo organizados por contexto."""

from pathlib import Path
import json
import random
import csv
from io import StringIO
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta, timezone


Chunk = Dict[str, str]


# Chunks base pré-carregados
BASE_CHUNKS: List[Chunk] = [
    {
        "id": "chunk_001",
        "context": "Conversação Básica",
        "content": "How are you doing today?",
        "translation": "Como você está hoje?",
        "when_to_use": "Cumprimento informal e amigável no dia a dia.",
        "difficulty": "beginner",
        "tags": ["greeting", "daily", "informal"],
        "examples": "How are you doing today? Pretty good, thanks!",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_002",
        "context": "Conversação Básica",
        "content": "What do you do for a living?",
        "translation": "O que você faz para viver?",
        "when_to_use": "Pergunta comum ao conhecer alguém em contexto social ou profissional.",
        "difficulty": "beginner",
        "tags": ["introduction", "work", "social"],
        "examples": "What do you do for a living? I'm a software engineer.",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_003",
        "context": "Negócios",
        "content": "Let's schedule a meeting to discuss this further.",
        "translation": "Vamos agendar uma reunião para discutir isso mais detalhadamente.",
        "when_to_use": "Ambiente profissional quando precisa aprofundar uma discussão.",
        "difficulty": "intermediate",
        "tags": ["business", "meeting", "professional"],
        "examples": "Let's schedule a meeting to discuss this further. How about Tuesday?",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_004",
        "context": "Restaurante",
        "content": "Could I have the bill, please?",
        "translation": "Poderia me trazer a conta, por favor?",
        "when_to_use": "Ao final de uma refeição para pedir a conta no restaurante.",
        "difficulty": "beginner",
        "tags": ["restaurant", "dining", "polite"],
        "examples": "Could I have the bill, please? Keep the change.",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_005",
        "context": "Viagem",
        "content": "Where is the nearest subway station?",
        "translation": "Onde fica a estação de metrô mais próxima?",
        "when_to_use": "Quando precisa de informações sobre transporte público em cidade desconhecida.",
        "difficulty": "beginner",
        "tags": ["travel", "transport", "directions"],
        "examples": "Where is the nearest subway station? It's two blocks from here.",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_006",
        "context": "Acadêmico",
        "content": "Could you elaborate on that point?",
        "translation": "Você poderia elaborar mais sobre esse ponto?",
        "when_to_use": "Em aulas ou reuniões quando quer entender melhor um tópico específico.",
        "difficulty": "intermediate",
        "tags": ["academic", "learning", "formal"],
        "examples": "Could you elaborate on that point? I didn't quite catch it.",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_007",
        "context": "Social",
        "content": "I'm really looking forward to the weekend.",
        "translation": "Estou realmente ansioso para o fim de semana.",
        "when_to_use": "Expressar entusiasmo sobre eventos futuros ou planos.",
        "difficulty": "intermediate",
        "tags": ["social", "plans", "emotion"],
        "examples": "I'm really looking forward to the weekend. We have a party to attend.",
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "chunk_008",
        "context": "Profissional",
        "content": "I'll get back to you by end of day.",
        "translation": "Te dou retorno até o final do dia.",
        "when_to_use": "Prometer retorno com prazo definido em ambiente de trabalho.",
        "difficulty": "intermediate",
        "tags": ["business", "deadline", "communication"],
        "examples": "I'll get back to you by end of day with the report.",
        "created_at": "2024-01-01T00:00:00Z"
    },
]


# Arquivos de persistência
CHUNKS_FILE = Path(__file__).with_name("chuncks_data.json")
ONLINE_CACHE_FILE = Path(__file__).with_name("chuncks_online_cache.json")
STUDY_PROGRESS_FILE = Path(__file__).with_name("chuncks_study_progress.json")


def _generate_chunk_id() -> str:
    """Gera ID único para um novo chunk."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = random.randint(1000, 9999)
    return f"chunk_{timestamp}_{random_suffix}"


def _validate_chunk(chunk: Dict) -> bool:
    """Valida se um chunk tem todos os campos obrigatórios."""
    required_fields = ["context", "content", "translation"]
    return all(field in chunk and str(chunk[field]).strip() for field in required_fields)


def _normalize_chunk(chunk: Dict) -> Optional[Chunk]:
    """Normaliza e valida um chunk."""
    if not isinstance(chunk, dict):
        return None
    
    context = str(chunk.get("context", "")).strip()
    content = str(chunk.get("content", "")).strip()
    translation = str(chunk.get("translation", "")).strip()
    
    if not context or not content or not translation:
        return None
    
    normalized: Chunk = {
        "id": str(chunk.get("id", _generate_chunk_id())).strip(),
        "context": context,
        "content": content,
        "translation": translation,
        "when_to_use": str(chunk.get("when_to_use", "")).strip(),
        "difficulty": str(chunk.get("difficulty", "intermediate")).strip().lower(),
        "tags": [str(t).strip() for t in chunk.get("tags", []) if str(t).strip()],
        "examples": str(chunk.get("examples", "")).strip(),
        "created_at": str(chunk.get("created_at", datetime.now(timezone.utc).isoformat())).strip(),
    }
    
    return normalized


# ==================== GERENCIAMENTO DE ARQUIVO LOCAL ====================

def load_chunks() -> List[Chunk]:
    """Carrega todos os chunks salvos localmente (base + customizados)."""
    if not CHUNKS_FILE.exists():
        return BASE_CHUNKS.copy()
    
    try:
        with CHUNKS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return BASE_CHUNKS.copy()
    
    if not isinstance(data, list):
        return BASE_CHUNKS.copy()
    
    custom_chunks = []
    existing_ids = {chunk["id"] for chunk in BASE_CHUNKS}
    
    for item in data:
        normalized = _normalize_chunk(item)
        if normalized and normalized["id"] not in existing_ids:
            custom_chunks.append(normalized)
            existing_ids.add(normalized["id"])
    
    return BASE_CHUNKS + custom_chunks



def _generate_chunk_id_from_base() -> str:
    """Helper para gerar IDs base (não utilizado diretamente)."""
    return "base"


def save_chunks(chunks: List[Chunk]) -> bool:
    """Salva apenas chunks customizados (não sobrescreve base)."""
    base_ids = {chunk["id"] for chunk in BASE_CHUNKS}
    custom_chunks = [chunk for chunk in chunks if chunk["id"] not in base_ids]
    
    try:
        with CHUNKS_FILE.open("w", encoding="utf-8") as file:
            json.dump(custom_chunks, file, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def add_chunk(chunk: Dict) -> tuple[bool, str]:
    """Adiciona um novo chunk customizado.
    
    Returns:
        tuple[bool, str]: (sucesso, mensagem)
    """
    normalized = _normalize_chunk(chunk)
    if not normalized:
        return False, "Chunk inválido. Verifique os campos obrigatórios: context, content, translation."
    
    existing = load_chunks()
    existing_ids = {c["id"] for c in existing}
    
    if normalized["id"] in existing_ids:
        return False, f"Chunk com ID '{normalized['id']}' já existe."
    
    existing.append(normalized)
    
    if save_chunks(existing):
        return True, f"Chunk '{normalized['id']}' adicionado com sucesso!"
    return False, "Erro ao salvar chunk."


def add_chunks_bulk(chunks: List[Dict]) -> Dict[str, int]:
    """Adiciona múltiplos chunks em lote.
    
    Returns:
        Dict com estatísticas: added, duplicates, invalid
    """
    existing = load_chunks()
    existing_ids = {c["id"] for c in existing}
    
    stats = {"added": 0, "duplicates": 0, "invalid": 0}
    
    for chunk in chunks:
        normalized = _normalize_chunk(chunk)
        if not normalized:
            stats["invalid"] += 1
            continue
        
        if normalized["id"] in existing_ids:
            stats["duplicates"] += 1
            continue
        
        existing.append(normalized)
        existing_ids.add(normalized["id"])
        stats["added"] += 1
    
    if stats["added"] > 0:
        save_chunks(existing)
    
    return stats


def delete_chunk(chunk_id: str) -> bool:
    """Remove um chunk customizado pelo ID."""
    if not chunk_id:
        return False
    
    existing = load_chunks()
    base_ids = {chunk["id"] for chunk in BASE_CHUNKS}
    
    # Protege chunks base
    if chunk_id in base_ids:
        return False
    
    filtered = [c for c in existing if c["id"] != chunk_id]
    
    if len(filtered) == len(existing):
        return False
    
    return save_chunks(filtered)


def get_chunk_by_id(chunk_id: str) -> Optional[Chunk]:
    """Busca um chunk específico pelo ID."""
    for chunk in load_chunks():
        if chunk["id"] == chunk_id:
            return chunk
    return None


# ==================== FILTROS E CONSULTAS ====================

def list_contexts() -> List[str]:
    """Retorna lista de contextos disponíveis."""
    return sorted({chunk["context"] for chunk in load_chunks()})


def filter_chunks(context: str = "Todos", difficulty: str = "Todos", tags: List[str] = None) -> List[Chunk]:
    """Filtra chunks por contexto, dificuldade e tags."""
    chunks = load_chunks()
    
    if context != "Todos":
        chunks = [c for c in chunks if c["context"] == context]
    
    if difficulty != "Todos":
        chunks = [c for c in chunks if c["difficulty"] == difficulty.lower()]
    
    if tags:
        tags_lower = [t.lower() for t in tags]
        chunks = [c for c in chunks if any(tag.lower() in tags_lower for tag in c.get("tags", []))]
    
    return chunks


def search_chunks(query: str) -> List[Chunk]:
    """Busca chunks por texto em content, translation ou context."""
    query_lower = query.lower().strip()
    if not query_lower:
        return []
    
    results = []
    for chunk in load_chunks():
        searchable = f"{chunk['content']} {chunk['translation']} {chunk['context']}".lower()
        if query_lower in searchable:
            results.append(chunk)
    
    return results


def get_random_chunks(limit: int = 5, context: str = "Todos", difficulty: str = "Todos") -> List[Chunk]:
    """Retorna chunks aleatórios com filtros opcionais."""
    filtered = filter_chunks(context, difficulty)
    
    if not filtered:
        return []
    
    return random.sample(filtered, min(limit, len(filtered)))


# ==================== UPLOAD DE ARQUIVOS ====================

def parse_chunks_json(content: str) -> List[Chunk]:
    """Parse de arquivo JSON contendo chunks."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []
    
    if isinstance(data, dict):
        data = [data]
    
    if not isinstance(data, list):
        return []
    
    valid_chunks = []
    for item in data:
        normalized = _normalize_chunk(item)
        if normalized:
            valid_chunks.append(normalized)
    
    return valid_chunks


def parse_chunks_csv(content: str) -> List[Chunk]:
    """Parse de arquivo CSV contendo chunks."""
    try:
        reader = csv.DictReader(StringIO(content))
        chunks = []
        
        for row in reader:
            chunk = {
                "context": (row.get("context") or "").strip(),
                "content": (row.get("content") or "").strip(),
                "translation": (row.get("translation") or "").strip(),
                "when_to_use": (row.get("when_to_use") or "").strip(),
                "difficulty": (row.get("difficulty") or "intermediate").strip().lower(),
                "tags": [t.strip() for t in (row.get("tags") or "").split(",") if t.strip()],
                "examples": (row.get("examples") or "").strip(),
            }
            
            normalized = _normalize_chunk(chunk)
            if normalized:
                chunks.append(normalized)
        
        return chunks
    except Exception:
        return []


def upload_chunks_from_file(content: str, file_format: str = "json") -> Dict[str, int]:
    """Faz upload de chunks a partir de arquivo.
    
    Args:
        content: Conteúdo do arquivo
        file_format: 'json' ou 'csv'
    
    Returns:
        Dict com estatísticas: added, duplicates, invalid
    """
    if file_format.lower() == "csv":
        chunks = parse_chunks_csv(content)
    else:
        chunks = parse_chunks_json(content)
    
    return add_chunks_bulk(chunks)


# ==================== DOWNLOAD E EXPORTAÇÃO ====================

def export_chunks_json() -> str:
    """Exporta todos os chunks em formato JSON."""
    return json.dumps(load_chunks(), ensure_ascii=False, indent=2)


def export_chunks_csv() -> str:
    """Exporta todos os chunks em formato CSV."""
    output = StringIO()
    fieldnames = ["id", "context", "content", "translation", "when_to_use", 
                  "difficulty", "tags", "examples", "created_at"]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for chunk in load_chunks():
        row = {
            "id": chunk.get("id", ""),
            "context": chunk.get("context", ""),
            "content": chunk.get("content", ""),
            "translation": chunk.get("translation", ""),
            "when_to_use": chunk.get("when_to_use", ""),
            "difficulty": chunk.get("difficulty", ""),
            "tags": ",".join(chunk.get("tags", [])),
            "examples": chunk.get("examples", ""),
            "created_at": chunk.get("created_at", ""),
        }
        writer.writerow(row)
    
    return output.getvalue()


def export_chunks_by_context(context: str) -> str:
    """Exporta chunks de um contexto específico em JSON."""
    chunks = filter_chunks(context)
    return json.dumps(chunks, ensure_ascii=False, indent=2)


# ==================== RECEPÇÃO ONLINE ====================

def _load_online_cache() -> Dict:
    """Carrega cache de chunks online."""
    if not ONLINE_CACHE_FILE.exists():
        return {}
    
    try:
        with ONLINE_CACHE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_online_cache(chunks: List[Chunk]) -> None:
    """Salva chunks online no cache."""
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "chunks": chunks,
    }
    with ONLINE_CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _is_cache_fresh(updated_at_iso: str, hours: int = 24) -> bool:
    """Verifica se cache está fresco."""
    try:
        updated_at = datetime.fromisoformat(updated_at_iso)
    except ValueError:
        return False
    
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    
    return datetime.now(timezone.utc) - updated_at < timedelta(hours=hours)


def fetch_online_chunks(limit: int = 5, force_refresh: bool = False) -> List[Chunk]:
    """Busca chunks online de APIs públicas.
    
    Args:
        limit: Número máximo de chunks a buscar
        force_refresh: Se True, ignora cache e busca novamente
    
    Returns:
        Lista de chunks online
    """
    cache = _load_online_cache()
    
    # Verifica cache
    if not force_refresh:
        cached_chunks = cache.get("chunks", [])
        updated_at = cache.get("updated_at", "")
        
        if cached_chunks and _is_cache_fresh(updated_at):
            return cached_chunks[:limit]
    
    # Busca novas frases online
    new_chunks = _fetch_chunks_from_apis(limit)
    
    if new_chunks:
        _save_online_cache(new_chunks)
    
    return new_chunks[:limit]


def _fetch_chunks_from_apis(limit: int) -> List[Chunk]:
    """Busca chunks de APIs públicas."""
    candidates: List[Chunk] = []
    
    # API 1: Frases de idiomas (Tatoeba-like)
    try:
        response = requests.get(
            "https://api.tatoeba.org/stable/en/sentences",
            params={
                "lang": "eng",
                "limit": min(limit, 10),
                "random": "true",
                "has_audio": "true"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        for sentence in data.get("sentences", [])[:limit]:
            text = sentence.get("text", "").strip()
            if text and len(text) > 10:
                candidates.append({
                    "id": _generate_chunk_id(),
                    "context": "Frases da Internet",
                    "content": text,
                    "translation": "",
                    "when_to_use": "Frase autêntica de uso real em inglês.",
                    "difficulty": "intermediate",
                    "tags": ["online", "authentic"],
                    "examples": text,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
    except (requests.RequestException, ValueError, KeyError):
        pass
    
    # API 2: Quotes inspiradores (fallback)
    if len(candidates) < limit:
        try:
            response = requests.get(
                "https://api.quotable.io/random",
                params={"minLength": 20, "maxLength": 100},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            quote = data.get("content", "").strip()
            author = data.get("author", "Unknown")
            
            if quote:
                candidates.append({
                    "id": _generate_chunk_id(),
                    "context": "Citações",
                    "content": quote,
                    "translation": "",
                    "when_to_use": f"Citação de {author} para reflexão e aprendizado.",
                    "difficulty": "intermediate",
                    "tags": ["quote", "inspiration", author.replace(" ", "_")],
                    "examples": f"{quote} - {author}",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
        except (requests.RequestException, ValueError, KeyError):
            pass
    
    # Remove duplicatas
    existing_ids = {c["id"] for c in load_chunks()}
    unique = []
    seen = set()
    
    for chunk in candidates:
        content_id = chunk["content"].lower().strip()
        if content_id not in seen and chunk["id"] not in existing_ids:
            seen.add(content_id)
            unique.append(chunk)
    
    return unique[:limit]


def incorporate_online_chunks(limit: int = 3) -> int:
    """Busca e incorpora chunks online automaticamente.
    
    Returns:
        Número de chunks adicionados
    """
    online_chunks = fetch_online_chunks(limit)
    
    if not online_chunks:
        return 0
    
    stats = add_chunks_bulk(online_chunks)
    return stats["added"]


def get_online_cache_info() -> Dict[str, str]:
    """Retorna informações sobre o cache online."""
    cache = _load_online_cache()
    updated_at = cache.get("updated_at", "")
    chunks = cache.get("chunks", [])
    
    if not updated_at:
        return {"status": "Sem cache", "updated_at": "-", "count": "0"}
    
    status = "Válido" if _is_cache_fresh(updated_at) else "Expirado"
    return {
        "status": status,
        "updated_at": updated_at,
        "count": str(len(chunks))
    }


# ==================== PROGRESSO DE ESTUDO ====================

def _load_study_progress() -> Dict:
    """Carrega progresso de estudo do usuário."""
    if not STUDY_PROGRESS_FILE.exists():
        return {}
    
    try:
        with STUDY_PROGRESS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_study_progress(progress: Dict) -> None:
    """Salva progresso de estudo."""
    with STUDY_PROGRESS_FILE.open("w", encoding="utf-8") as file:
        json.dump(progress, file, ensure_ascii=False, indent=2)


def record_study_session(chunk_id: str, success: bool, time_spent: float = 0.0) -> None:
    """Registra uma sessão de estudo de um chunk.
    
    Args:
        chunk_id: ID do chunk estudado
        success: Se o usuário acertou/dominou o chunk
        time_spent: Tempo gasto em segundos
    """
    progress = _load_study_progress()
    
    if chunk_id not in progress:
        progress[chunk_id] = {
            "reviews": 0,
            "successes": 0,
            "last_review": None,
            "next_review": None,
            "total_time": 0.0,
            "difficulty_score": 2.5,  # Inicial (escala 0-5)
        }
    
    chunk_progress = progress[chunk_id]
    chunk_progress["reviews"] += 1
    chunk_progress["total_time"] += time_spent
    
    if success:
        chunk_progress["successes"] += 1
        # Aumenta dificuldade (mais fácil = próxima revisão mais tarde)
        chunk_progress["difficulty_score"] = min(5.0, chunk_progress["difficulty_score"] + 0.5)
    else:
        # Diminui dificuldade (mais difícil = próxima revisão mais cedo)
        chunk_progress["difficulty_score"] = max(0.0, chunk_progress["difficulty_score"] - 0.8)
    
    chunk_progress["last_review"] = datetime.now(timezone.utc).isoformat()
    
    # Calcula próxima revisão baseado em spaced repetition
    days_until_next = _calculate_review_interval(chunk_progress["difficulty_score"])
    next_review = datetime.now(timezone.utc) + timedelta(days=days_until_next)
    chunk_progress["next_review"] = next_review.isoformat()
    
    _save_study_progress(progress)


def _calculate_review_interval(difficulty_score: float) -> int:
    """Calcula intervalo até próxima revisão (em dias)."""
    # Baseado em algoritmo SM-2 simplificado
    intervals = [1, 3, 7, 14, 21, 30, 45, 60]
    index = min(int(difficulty_score), len(intervals) - 1)
    return intervals[index]


def get_chunks_to_review() -> List[tuple[Chunk, Dict]]:
    """Retorna chunks que precisam de revisão hoje.
    
    Returns:
        Lista de tuplas (chunk, progresso)
    """
    progress = _load_study_progress()
    now = datetime.now(timezone.utc)
    
    to_review = []
    for chunk in load_chunks():
        chunk_progress = progress.get(chunk["id"], {})
        next_review_str = chunk_progress.get("next_review")
        
        if not next_review_str:
            # Nunca revisado - adiciona à fila
            to_review.append((chunk, chunk_progress))
            continue
        
        try:
            next_review = datetime.fromisoformat(next_review_str)
            if next_review.tzinfo is None:
                next_review = next_review.replace(tzinfo=timezone.utc)
            
            if now >= next_review:
                to_review.append((chunk, chunk_progress))
        except (ValueError, TypeError):
            continue
    
    return to_review


def get_study_statistics() -> Dict:
    """Retorna estatísticas de estudo do usuário."""
    progress = _load_study_progress()
    all_chunks = load_chunks()
    
    total_chunks = len(all_chunks)
    studied_chunks = len(progress)
    
    total_reviews = sum(p.get("reviews", 0) for p in progress.values())
    total_successes = sum(p.get("successes", 0) for p in progress.values())
    
    success_rate = (total_successes / total_reviews * 100) if total_reviews > 0 else 0.0
    
    total_time = sum(p.get("total_time", 0.0) for p in progress.values())
    
    # Chunks por dificuldade
    difficulty_counts = {}
    for chunk in all_chunks:
        diff = chunk.get("difficulty", "intermediate")
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    # Chunks por contexto
    context_counts = {}
    for chunk in all_chunks:
        ctx = chunk.get("context", "Outros")
        context_counts[ctx] = context_counts.get(ctx, 0) + 1
    
    return {
        "total_chunks": total_chunks,
        "studied_chunks": studied_chunks,
        "not_studied": total_chunks - studied_chunks,
        "total_reviews": total_reviews,
        "success_rate": round(success_rate, 1),
        "total_time_minutes": round(total_time / 60, 1),
        "difficulty_distribution": difficulty_counts,
        "context_distribution": context_counts,
        "chunks_to_review_today": len(get_chunks_to_review()),
    }


def reset_study_progress(chunk_id: Optional[str] = None) -> bool:
    """Reseta progresso de estudo.
    
    Args:
        chunk_id: Se fornecido, reseta apenas esse chunk. Senão, reseta tudo.
    
    Returns:
        True se sucesso
    """
    if chunk_id:
        progress = _load_study_progress()
        if chunk_id in progress:
            del progress[chunk_id]
            _save_study_progress(progress)
            return True
        return False
    else:
        # Reseta tudo
        _save_study_progress({})
        return True


# ==================== SISTEMA DE REVISÃO ESPAÇADA ====================

def get_study_queue(limit: int = 10) -> List[Chunk]:
    """Retorna fila de estudo priorizada por spaced repetition.
    
    Prioridade:
    1. Chunks não estudados
    2. Chunks com revisão vencida
    3. Chunks por ordem de dificuldade
    """
    to_review = get_chunks_to_review()
    all_chunks = load_chunks()
    progress = _load_study_progress()
    
    # Separa não estudados
    studied_ids = set(progress.keys())
    not_studied = [c for c in all_chunks if c["id"] not in studied_ids]
    
    # Ordena revisões por dificuldade (mais difícil primeiro)
    to_review_sorted = sorted(to_review, key=lambda x: x[1].get("difficulty_score", 2.5))
    
    # Combina lista
    queue = [c for c, _ in to_review_sorted] + not_studied
    
    return queue[:limit]


# ==================== UTILITÁRIOS ====================

def get_chunk_count() -> int:
    """Retorna número total de chunks."""
    return len(load_chunks())


def get_chunks_by_difficulty(difficulty: str) -> List[Chunk]:
    """Retorna chunks de uma dificuldade específica."""
    return [c for c in load_chunks() if c.get("difficulty") == difficulty.lower()]


def get_chunks_by_tag(tag: str) -> List[Chunk]:
    """Retorna chunks com uma tag específica."""
    tag_lower = tag.lower()
    return [c for c in load_chunks() if any(t.lower() == tag_lower for t in c.get("tags", []))]


def validate_chunks_file(content: str, file_format: str) -> Dict[str, any]:
    """Valida arquivo de chunks antes do upload.
    
    Returns:
        Dict com: valid (bool), total (int), valid_chunks (int), errors (List[str])
    """
    try:
        if file_format.lower() == "csv":
            chunks = parse_chunks_csv(content)
        else:
            chunks = parse_chunks_json(content)
        
        valid_count = sum(1 for c in chunks if _validate_chunk(c))
        
        return {
            "valid": valid_count > 0,
            "total": len(chunks),
            "valid_chunks": valid_count,
            "errors": [f"Chunk {i+1}: inválido" for i, c in enumerate(chunks) if not _validate_chunk(c)]
        }
    except Exception as e:
        return {
            "valid": False,
            "total": 0,
            "valid_chunks": 0,
            "errors": [str(e)]
        }


# ==================== EXPORTAÇÃO DE DADOS PARA ESTUDO ====================

def generate_study_flashcards(limit: int = 20, context: str = "Todos") -> List[Dict]:
    """Gera flashcards para estudo (formato simples).
    
    Returns:
        Lista de dicts com: front, back, context, difficulty
    """
    chunks = filter_chunks(context)
    
    if not chunks:
        return []
    
    selected = random.sample(chunks, min(limit, len(chunks)))
    
    flashcards = []
    for chunk in selected:
        flashcards.append({
            "front": chunk["content"],
            "back": chunk["translation"],
            "context": chunk["context"],
            "difficulty": chunk["difficulty"],
            "when_to_use": chunk.get("when_to_use", ""),
        })
    
    return flashcards


def generate_quiz_questions(limit: int = 10, context: str = "Todos") -> List[Dict]:
    """Gera perguntas de quiz para auto-avaliação.
    
    Returns:
        Lista de dicts com: question, options, correct_answer, explanation
    """
    chunks = filter_chunks(context)
    
    if len(chunks) < 4:
        return []
    
    selected = random.sample(chunks, min(limit, len(chunks)))
    questions = []
    
    for chunk in selected:
        # Gera 3 alternativas erradas
        other_chunks = [c for c in chunks if c["id"] != chunk["id"]]
        wrong_options = random.sample(other_chunks, min(3, len(other_chunks)))
        
        options = [chunk["translation"]] + [c["translation"] for c in wrong_options]
        random.shuffle(options)
        
        questions.append({
            "question": f"Qual a tradução de: '{chunk['content']}'?",
            "options": options,
            "correct_answer": chunk["translation"],
            "explanation": chunk.get("when_to_use", ""),
            "context": chunk["context"],
        })
    
    return questions


# ==================== INTEGRAÇÃO COM OUTROS MÓDULOS ====================

def get_chunks_suggestions_for_context(context: str, limit: int = 5) -> List[Chunk]:
    """Sugere chunks relevantes para um contexto específico.
    
    Útil para integração com daily_phrases e outros módulos.
    """
    # Prioriza chunks do contexto exato
    exact_match = filter_chunks(context)
    
    # Se não houver suficientes, busca por tags relacionadas
    if len(exact_match) < limit:
        # Busca chunks com tags similares
        all_chunks = load_chunks()
        context_words = context.lower().split()
        
        tag_matches = []
        for chunk in all_chunks:
            if chunk["id"] in [c["id"] for c in exact_match]:
                continue
            
            tags = [t.lower() for t in chunk.get("tags", [])]
            if any(word in tags for word in context_words):
                tag_matches.append(chunk)
        
        exact_match.extend(tag_matches[:limit - len(exact_match)])
    
    return exact_match[:limit]


# ==================== ESTATÍSTICAS AVANÇADAS ====================

def get_learning_insights() -> Dict:
    """Retorna insights personalizados sobre o aprendizado."""
    stats = get_study_statistics()
    progress = _load_study_progress()
    
    # Chunks difíceis (menor taxa de sucesso)
    difficult_chunks = []
    for chunk_id, chunk_progress in progress.items():
        if chunk_progress.get("reviews", 0) >= 3:
            success_rate = chunk_progress.get("successes", 0) / chunk_progress.get("reviews", 1)
            if success_rate < 0.5:
                chunk = get_chunk_by_id(chunk_id)
                if chunk:
                    difficult_chunks.append({
                        "content": chunk["content"],
                        "success_rate": round(success_rate * 100, 1),
                        "reviews": chunk_progress.get("reviews", 0)
                    })
    
    # Chunks dominados (100% sucesso)
    mastered_chunks = []
    for chunk_id, chunk_progress in progress.items():
        if chunk_progress.get("reviews", 0) >= 5:
            success_rate = chunk_progress.get("successes", 0) / chunk_progress.get("reviews", 1)
            if success_rate >= 0.9:
                chunk = get_chunk_by_id(chunk_id)
                if chunk:
                    mastered_chunks.append(chunk["content"])
    
    # Recomendações
    recommendations = []
    if stats["not_studied"] > 0:
        recommendations.append(f"Você tem {stats['not_studied']} chunks novos para estudar!")
    
    if stats["chunks_to_review_today"] > 0:
        recommendations.append(f"Revise {stats['chunks_to_review_today']} chunks hoje para manter o progresso.")
    
    if stats["success_rate"] < 60:
        recommendations.append("Considere revisar os chunks mais difíceis antes de avançar.")
    
    if stats["total_time_minutes"] > 30:
        recommendations.append("Ótimo ritmo de estudos! Considere fazer pausas regulares.")
    
    return {
        "difficult_chunks": difficult_chunks[:5],
        "mastered_chunks": mastered_chunks[:10],
        "recommendations": recommendations,
        "streak_days": _calculate_streak(progress),
    }


def _calculate_streak(progress: Dict) -> int:
    """Calcula dias consecutivos de estudo (simplificado)."""
    if not progress:
        return 0
    
    # Conta dias únicos de estudo
    study_dates = set()
    for chunk_progress in progress.values():
        last_review = chunk_progress.get("last_review")
        if last_review:
            try:
                date = datetime.fromisoformat(last_review).date()
                study_dates.add(date)
            except (ValueError, TypeError):
                continue
    
    if not study_dates:
        return 0
    
    # Calcula streak
    sorted_dates = sorted(study_dates, reverse=True)
    today = datetime.now(timezone.utc).date()
    
    streak = 0
    check_date = today
    
    for study_date in sorted_dates:
        if study_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif study_date < check_date:
            break
    
    return streak


# ==================== INICIALIZAÇÃO ====================

def initialize_module() -> Dict[str, any]:
    """Inicializa o módulo e retorna status."""
    chunks = load_chunks()
    cache_info = get_online_cache_info()
    stats = get_study_statistics()
    
    return {
        "status": "initialized",
        "total_chunks": len(chunks),
        "base_chunks": len(BASE_CHUNKS),
        "custom_chunks": len(chunks) - len(BASE_CHUNKS),
        "contexts": list_contexts(),
        "cache_info": cache_info,
        "study_stats": stats,
    }


# Inicializa módulo ao importar
if __name__ != "__main__":
    try:
        _module_status = initialize_module()
    except Exception:
        _module_status = {"status": "error"}