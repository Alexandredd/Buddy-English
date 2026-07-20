"""Módulo de Vocabulário por Contexto - Inglês Americano com exemplos bilíngues."""

import json
import random
import os
from pathlib import Path
from datetime import datetime, timezone

VOCABULARY_FILE = Path(__file__).with_name("vocabulary_data.json")


def load_vocabulary():
    """Carrega o vocabulário do arquivo JSON."""
    if not VOCABULARY_FILE.exists():
        return []
    try:
        with VOCABULARY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_vocabulary(vocab_list):
    """Salva o vocabulário no arquivo JSON."""
    with VOCABULARY_FILE.open("w", encoding="utf-8") as file:
        json.dump(vocab_list, file, ensure_ascii=False, indent=2)


def add_vocabulary_item(word, context, translation, examples, notes=""):
    """Adiciona um item ao vocabulário.
    
    Args:
        word: Palavra ou expressão em inglês
        context: Contexto de uso (ex: "Restaurante", "Trabalho", "Viagem")
        translation: Tradução principal em português
        examples: Lista de dicionários com exemplos de uso
                  [{"english": "...", "portuguese": "..."}]
        notes: Notas adicionais sobre uso (opcional)
    
    Returns:
        dict: Item adicionado ou None se já existir
    """
    vocab_list = load_vocabulary()
    
    # Verifica se já existe
    for item in vocab_list:
        if item["word"].lower() == word.lower() and item["context"].lower() == context.lower():
            return None
    
    new_item = {
        "word": word.strip(),
        "context": context.strip(),
        "translation": translation.strip(),
        "examples": examples,
        "notes": notes.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    vocab_list.append(new_item)
    save_vocabulary(vocab_list)
    return new_item


def search_vocabulary(query, context=None):
    """Busca palavras no vocabulário.
    
    Args:
        query: Termo de busca (palavra ou tradução)
        context: Filtro por contexto (opcional)
    
    Returns:
        list: Lista de itens encontrados
    """
    vocab_list = load_vocabulary()
    query_lower = query.lower().strip()
    
    results = []
    for item in vocab_list:
        # Filtro por contexto
        if context and context != "Todos" and item["context"].lower() != context.lower():
            continue
        
        # Busca em palavra, tradução ou exemplos
        if (query_lower in item["word"].lower() or
            query_lower in item["translation"].lower() or
            any(query_lower in ex["english"].lower() or query_lower in ex["portuguese"].lower() 
                for ex in item.get("examples", []))):
            results.append(item)
    
    return results


def get_vocabulary_by_context(context):
    """Retorna todas as palavras de um contexto específico.
    
    Args:
        context: Nome do contexto
    
    Returns:
        list: Lista de itens do contexto
    """
    vocab_list = load_vocabulary()
    return [item for item in vocab_list if item["context"].lower() == context.lower()]


def list_contexts():
    """Lista todos os contextos disponíveis.
    
    Returns:
        list: Lista de contextos únicos
    """
    vocab_list = load_vocabulary()
    contexts = set(item["context"] for item in vocab_list)
    return sorted(list(contexts))


def get_random_examples(context=None, limit=5):
    """Retorna exemplos aleatórios do vocabulário.
    
    Args:
        context: Filtro por contexto (opcional)
        limit: Quantidade máxima de exemplos
    
    Returns:
        list: Lista de exemplos bilíngues
    """
    vocab_list = load_vocabulary()
    
    if context and context != "Todos":
        vocab_list = [item for item in vocab_list if item["context"].lower() == context.lower()]
    
    if not vocab_list:
        return []
    
    selected = random.sample(vocab_list, min(limit, len(vocab_list)))
    
    examples = []
    for item in selected:
        # Adiciona a palavra principal
        examples.append({
            "type": "word",
            "word": item["word"],
            "translation": item["translation"],
            "context": item["context"],
            "notes": item.get("notes", ""),
        })
        
        # Adiciona exemplos de frases
        for ex in item.get("examples", [])[:2]:  # Máximo 2 exemplos por palavra
            examples.append({
                "type": "example",
                "english": ex["english"],
                "portuguese": ex["portuguese"],
                "word": item["word"],
                "context": item["context"],
            })
    
    return examples


def generate_context_text(context, word_count=10):
    """Gera um texto de exemplo usando palavras de um contexto específico.
    
    Args:
        context: Nome do contexto
        word_count: Quantidade aproximada de palavras no texto
    
    Returns:
        dict: Texto bilíngue com palavras destacadas
    """
    vocab_list = get_vocabulary_by_context(context)
    
    if not vocab_list:
        return None
    
    # Seleciona palavras aleatórias do contexto
    selected_words = random.sample(vocab_list, min(5, len(vocab_list)))
    
    # Gera texto simples em inglês
    english_parts = []
    portuguese_parts = []
    
    for item in selected_words:
        # Usa o primeiro exemplo se disponível, senão cria um simples
        if item.get("examples"):
            ex = item["examples"][0]
            english_parts.append(ex["english"])
            portuguese_parts.append(ex["portuguese"])
        else:
            # Cria exemplo simples
            eng = f"I learned about {item['word']}."
            pt = f"Aprendi sobre {item['translation']}."
            english_parts.append(eng)
            portuguese_parts.append(pt)
    
    english_text = " ".join(english_parts)
    portuguese_text = " ".join(portuguese_parts)
    
    return {
        "english": english_text,
        "portuguese": portuguese_text,
        "context": context,
        "words_used": [item["word"] for item in selected_words],
    }


def get_vocabulary_stats():
    """Retorna estatísticas do vocabulário.
    
    Returns:
        dict: Estatísticas (total, por contexto, etc.)
    """
    vocab_list = load_vocabulary()
    
    stats = {
        "total_words": len(vocab_list),
        "contexts": {},
        "total_examples": 0,
    }
    
    for item in vocab_list:
        context = item["context"]
        if context not in stats["contexts"]:
            stats["contexts"][context] = 0
        stats["contexts"][context] += 1
        stats["total_examples"] += len(item.get("examples", []))
    
    return stats


def import_vocabulary_from_json(json_content):
    """Importa vocabulário de um arquivo JSON.
    
    Formato esperado:
    [
        {
            "word": "hello",
            "context": "Greeting",
            "translation": "olá",
            "examples": [
                {"english": "Hello, how are you?", "portuguese": "Olá, como você está?"}
            ],
            "notes": "Informal greeting"
        }
    ]
    
    Returns:
        dict: Resumo da importação
    """
    try:
        data = json.loads(json_content)
        if not isinstance(data, list):
            return {"added": 0, "duplicates": 0, "invalid": 0}
    except (json.JSONDecodeError, TypeError):
        return {"added": 0, "duplicates": 0, "invalid": 0}
    
    vocab_list = load_vocabulary()
    added = 0
    duplicates = 0
    invalid = 0
    
    for item in data:
        if not isinstance(item, dict):
            invalid += 1
            continue
        
        word = item.get("word", "").strip()
        context = item.get("context", "").strip()
        translation = item.get("translation", "").strip()
        examples = item.get("examples", [])
        notes = item.get("notes", "")
        
        if not word or not context or not translation:
            invalid += 1
            continue
        
        # Verifica duplicatas
        is_duplicate = any(
            v["word"].lower() == word.lower() and v["context"].lower() == context.lower()
            for v in vocab_list
        )
        
        if is_duplicate:
            duplicates += 1
            continue
        
        new_item = {
            "word": word,
            "context": context,
            "translation": translation,
            "examples": examples if isinstance(examples, list) else [],
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        vocab_list.append(new_item)
        added += 1
    
    save_vocabulary(vocab_list)
    return {"added": added, "duplicates": duplicates, "invalid": invalid}


def export_vocabulary_to_json():
    """Exporta todo o vocabulário para JSON.
    
    Returns:
        str: JSON string do vocabulário
    """
    vocab_list = load_vocabulary()
    return json.dumps(vocab_list, ensure_ascii=False, indent=2)


# Inicializa o arquivo se não existir
if not VOCABULARY_FILE.exists():
    save_vocabulary([])