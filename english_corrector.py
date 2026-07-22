"""
english_corrector.py
====================

Módulo de correção de inglês com IA para o Buddy-English.

Este módulo implementa um assistente de correção de inglês para estudantes
brasileiros. Ele utiliza a API OpenAI (Chat Completions) para analisar um
texto em inglês e retornar, em português:

  1. Texto corrigido (gramática, ortografia, pontuação)
  2. Versão natural de nativo
  3. Explicação detalhada de cada erro
  4. Phrasal verbs e expressões idiomáticas sugeridas
  5. Novo vocabulário aprendido (palavra, tradução, classe, exemplo)

Também gerencia o histórico de correções em um arquivo JSON local.

Autor: Alexandredd
"""

import json
import os
import re
import html
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Constantes e configurações
# ---------------------------------------------------------------------------

# Arquivo onde o histórico de correções é persistido
CORRECTION_HISTORY_FILE = Path(__file__).with_name("correction_history.json")

# Número máximo de itens mantidos no histórico
MAX_HISTORY_ITEMS = 50

# Modelo padrão da OpenAI
DEFAULT_MODEL = "gpt-4o-mini"

# Endpoint da API OpenAI
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# ---------------------------------------------------------------------------
# Prompt do sistema (IA)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um professor de inglês especializado em ensinar brasileiros. Analise o texto enviado pelo usuário. Corrija gramática, ortografia e pontuação. Gere uma versão natural usada por falantes nativos. Explique todos os erros encontrados em português. Sugira phrasal verbs e expressões idiomáticas quando forem apropriados. Liste o novo vocabulário aprendido com tradução e exemplos. Responda sempre em português brasileiro.

Retorne APENAS um objeto JSON válido (sem markdown, sem explicações adicionais) com a seguinte estrutura:

{
  "texto_corrigido": "string com o texto corrigido",
  "versao_natural": "string com versão reescrita de forma natural",
  "explicacoes": [
    {
      "erro_original": "string",
      "correcao": "string",
      "explicacao": "string explicando a regra gramatical"
    }
  ],
  "phrasal_verbs": [
    {
      "expressao": "string",
      "significado": "string em português",
      "exemplo": "string em inglês"
    }
  ],
  "expressoes_idiomaticas": [
    {
      "expressao": "string",
      "significado": "string em português",
      "exemplo": "string em inglês"
    }
  ],
  "novo_vocabulario": [
    {
      "palavra": "string",
      "traducao": "string em português",
      "classe": "string (substantivo, verbo, adjetivo, etc.)",
      "exemplo": "string em inglês"
    }
  ]
}

Se não houver erros, retorne listas vazias para explicacoes, phrasal_verbs, expressoes_idiomaticas e novo_vocabulario. Se não houver phrasal verbs ou expressões idiomáticas apropriadas, retorne listas vazias."""


# ---------------------------------------------------------------------------
# Funções de API
# ---------------------------------------------------------------------------

def call_openai_correction(text, api_key, model=DEFAULT_MODEL, timeout=30):
    """
    Envia o texto para a API OpenAI e retorna a resposta bruta (string JSON).

    Parameters
    ----------
    text : str
        Texto em inglês a ser corrigido.
    api_key : str
        Chave da API OpenAI.
    model : str
        Modelo a ser usado (padrão: gpt-4o-mini).
    timeout : int
        Timeout em segundos para a requisição.

    Returns
    -------
    str
        Resposta da API (espera-se um JSON em texto).

    Raises
    ------
    requests.RequestException
        Se houver falha na comunicação com a API.
    ValueError
        Se a resposta não contiver conteúdo válido.
    """
    if not api_key:
        raise ValueError("Chave da API OpenAI não informada.")

    if not text or not text.strip():
        raise ValueError("Texto vazio para correção.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text.strip()},
    ]

    response = requests.post(
        OPENAI_ENDPOINT,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 4000,
        },
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()

    # Extrai o conteúdo da primeira escolha
    choices = data.get("choices", [])
    if not choices:
        raise ValueError("A API não retornou escolhas válidas.")

    content = choices[0].get("message", {}).get("content", "")
    if not content:
        raise ValueError("A API retornou conteúdo vazio.")

    return content.strip()


# ---------------------------------------------------------------------------
# Funções de parsing
# ---------------------------------------------------------------------------

def _extract_json_from_text(text):
    """
    Tenta extrair um objeto JSON de uma string que pode conter
    markdown ou texto adicional.

    Parameters
    ----------
    text : str
        Texto que contém (ou deveria conter) um JSON.

    Returns
    -------
    str
        A substring que parece ser JSON.
    """
    # Remove blocos de código markdown se presentes
    text = text.strip()

    # Tenta encontrar um bloco JSON entre ```json e ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)

    # Tenta encontrar o primeiro { e o último }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return text


def parse_ai_response(response_text):
    """
    Faz o parsing da resposta da IA em um dicionário estruturado.

    Parameters
    ----------
    response_text : str
        Resposta bruta da API (espera-se JSON).

    Returns
    -------
    dict
        Dicionário com as chaves: texto_corrigido, versao_natural,
        explicacoes, phrasal_verbs, expressoes_idiomaticas,
        novo_vocabulario.
    """
    # Tenta parsear diretamente
    try:
        data = json.loads(response_text)
    except (json.JSONDecodeError, TypeError):
        # Tenta extrair JSON do texto
        json_str = _extract_json_from_text(response_text)
        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            # Última tentativa: parse lento com correções comuns
            data = _try_repair_json(json_str)

    # Valida e normaliza a estrutura
    return _normalize_correction_data(data)


def _try_repair_json(json_str):
    """
    Tenta reparar JSON comuns problemas (vírgulas finais, aspas simples).
    """
    # Substitui aspas simples por aspas duplas (cuidado com strings internas)
    repaired = json_str

    # Remove vírgulas antes de } ou ]
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)

    try:
        return json.loads(repaired)
    except (json.JSONDecodeError, TypeError):
        return {}


def _normalize_correction_data(data):
    """
    Garante que o dicionário tenha todas as chaves esperadas com
    valores de tipo correto.
    """
    if not isinstance(data, dict):
        data = {}

    result = {
        "texto_corrigido": str(data.get("texto_corrigido", "")).strip(),
        "versao_natural": str(data.get("versao_natural", "")).strip(),
        "explicacoes": _ensure_list_of_dicts(data.get("explicacoes", [])),
        "phrasal_verbs": _ensure_list_of_dicts(data.get("phrasal_verbs", [])),
        "expressoes_idiomaticas": _ensure_list_of_dicts(
            data.get("expressoes_idiomaticas", [])
        ),
        "novo_vocabulario": _ensure_list_of_dicts(
            data.get("novo_vocabulario", [])
        ),
    }

    # Garante que texto_corrigido e versao_natural não sejam vazios
    if not result["texto_corrigido"]:
        result["texto_corrigido"] = "(sem correção disponível)"
    if not result["versao_natural"]:
        result["versao_natural"] = result["texto_corrigido"]

    return result


def _ensure_list_of_dicts(value):
    """
    Garante que o valor seja uma lista de dicionários.
    """
    if not isinstance(value, list):
        return []

    result = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# Funções de histórico
# ---------------------------------------------------------------------------

def save_correction_to_history(correction_data):
    """
    Salva uma correção no histórico (arquivo JSON local).

    Parameters
    ----------
    correction_data : dict
        Dados da correção (deve conter pelo menos 'original' e 'corrigido').

    Returns
    -------
    bool
        True se salvo com sucesso, False caso contrário.
    """
    try:
        history = load_correction_history()

        entry = {
            "id": _generate_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original": correction_data.get("original", ""),
            "texto_corrigido": correction_data.get("texto_corrigido", ""),
            "versao_natural": correction_data.get("versao_natural", ""),
            "explicacoes": correction_data.get("explicacoes", []),
            "phrasal_verbs": correction_data.get("phrasal_verbs", []),
            "expressoes_idiomaticas": correction_data.get(
                "expressoes_idiomaticas", []
            ),
            "novo_vocabulario": correction_data.get("novo_vocabulario", []),
        }

        history.insert(0, entry)

        # Mantém apenas os últimos MAX_HISTORY_ITEMS
        history = history[:MAX_HISTORY_ITEMS]

        with CORRECTION_HISTORY_FILE.open("w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        return True
    except Exception:
        return False


def load_correction_history():
    """
    Carrega o histórico de correções do arquivo JSON.

    Returns
    -------
    list
        Lista de dicionários com as correções salvas.
    """
    if not CORRECTION_HISTORY_FILE.exists():
        return []

    try:
        with CORRECTION_HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def clear_correction_history():
    """
    Limpa o histórico de correções.

    Returns
    -------
    bool
        True se limpo com sucesso, False caso contrário.
    """
    try:
        if CORRECTION_HISTORY_FILE.exists():
            CORRECTION_HISTORY_FILE.unlink()
        return True
    except Exception:
        return False


def _generate_id():
    """Gera um ID único baseado no timestamp e hash."""
    import hashlib

    raw = f"{datetime.now(timezone.utc).isoformat()}{os.urandom(8).hex()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Funções de UI (componentes reutilizáveis)
# ---------------------------------------------------------------------------

def render_copy_button(text_content, label="📋 Copiar", key="copy_btn"):
    """
    Renderiza um botão de cópia que copia o texto para a área de transferência.

    Parameters
    ----------
    text_content : str
        Texto a ser copiado.
    label : str
        Texto exibido no botão.
    key : str
        Chave única para identificar o botão no DOM.

    Returns
    -------
    str
        HTML do botão (para ser usado com st.markdown unsafe_allow_html=True).
    """
    # Escapa o texto para uso seguro em JavaScript
    escaped_json = json.dumps(text_content)

    button_html = f"""
    <button onclick="navigator.clipboard.writeText({escaped_json}).then(() => {{
        const btn = document.querySelector('[data-copy-key=\"{key}\"]');
        if (btn) {{
            const originalText = btn.innerText;
            btn.innerText = '✅ Copiado!';
            setTimeout(() => {{ btn.innerText = originalText; }}, 2000);
        }}
    }}).catch(err => {{
        console.error('Falha ao copiar: ', err);
        alert('Não foi possível copiar. Tente manualmente.');
    }})"
    data-copy-key="{key}"
    style="background: #f0f0f0; border: 1px solid #ddd; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 13px; margin-left: 8px; vertical-align: middle;">
    {label}
    </button>
    """
    return button_html


def render_text_with_copy(text_content, label="📋 Copiar", key="copy_btn"):
    """
    Renderiza um bloco de texto com um botão de cópia ao lado.

    Parameters
    ----------
    text_content : str
        Texto a ser exibido e copiado.
    label : str
        Texto do botão de cópia.
    key : str
        Chave única para o botão.
    """
    import streamlit as st

    # Exibe o texto em um bloco de código com botão de cópia integrado
    st.code(text_content, language="text")

    # Botão de cópia adicional
    st.markdown(render_copy_button(text_content, label=label, key=key), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Função principal de correção
# ---------------------------------------------------------------------------

def correct_english_text(text, api_key, model=DEFAULT_MODEL):
    """
    Função principal: corrige um texto em inglês usando IA.

    Parameters
    ----------
    text : str
        Texto em inglês a ser corrigido.
    api_key : str
        Chave da API OpenAI.
    model : str
        Modelo da OpenAI a ser usado.

    Returns
    -------
    dict
        Dicionário com:
        - 'success': bool
        - 'data': dict (dados da correção) ou None
        - 'error': str (mensagem de erro) ou None
    """
    if not text or not text.strip():
        return {
            "success": False,
            "data": None,
            "error": "Digite um texto em inglês para corrigir.",
        }

    if not api_key:
        return {
            "success": False,
            "data": None,
            "error": "Chave da API OpenAI não configurada. Configure a variável de ambiente OPENAI_API_KEY.",
        }

    try:
        # Chama a API
        response_text = call_openai_correction(text, api_key, model=model)

        # Faz o parsing da resposta
        correction_data = parse_ai_response(response_text)

        # Adiciona o texto original
        correction_data["original"] = text.strip()

        return {
            "success": True,
            "data": correction_data,
            "error": None,
        }

    except requests.RequestException as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Erro de conexão com a API: {str(exc)}",
        }
    except ValueError as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Erro ao processar a resposta da IA: {str(exc)}",
        }
    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Erro inesperado: {str(exc)}",
        }


# ---------------------------------------------------------------------------
# Função de fallback (correção local sem IA)
# ---------------------------------------------------------------------------

def correct_english_text_fallback(text):
    """
    Correção básica sem IA (usando LanguageTool + correções locais).

    Esta função é usada como fallback quando a API OpenAI não está disponível.
    Ela reutiliza as funções existentes do app.py.

    Parameters
    ----------
    text : str
        Texto em inglês a ser corrigido.

    Returns
    -------
    dict
        Dados da correção no mesmo formato do módulo de IA.
    """
    # Importa as funções do app.py (evita import circular)
    import importlib

    try:
        app_module = importlib.import_module("app")
        corrigir_texto = getattr(app_module, "corrigir_texto", None)
        correcao_local_basica = getattr(app_module, "correcao_local_basica", None)
    except Exception:
        corrigir_texto = None
        correcao_local_basica = None

    # Correção com LanguageTool (se disponível)
    texto_corrigido = text
    ajustes = []

    if corrigir_texto:
        try:
            result = corrigir_texto(text)
            texto_corrigido = result.get("texto_corrigido", text)
            ajustes = result.get("ajustes", [])
        except Exception:
            pass

    # Correção local adicional
    if correcao_local_basica:
        try:
            texto_corrigido, ajustes_locais = correcao_local_basica(texto_corrigido)
            ajustes.extend(ajustes_locais)
        except Exception:
            pass

    # Constrói explicações a partir dos ajustes
    explicacoes = []
    for ajuste in ajustes:
        explicacoes.append(
            {
                "erro_original": ajuste.get("de", ""),
                "correcao": ajuste.get("para", ""),
                "explicacao": ajuste.get("mensagem", "Ajuste sugerido."),
            }
        )

    return {
        "original": text.strip(),
        "texto_corrigido": texto_corrigido,
        "versao_natural": texto_corrigido,
        "explicacoes": explicacoes,
        "phrasal_verbs": [],
        "expressoes_idiomaticas": [],
        "novo_vocabulario": [],
    }


# ---------------------------------------------------------------------------
# Funções de formatação para exibição
# ---------------------------------------------------------------------------

def format_correction_for_display(correction_data):
    """
    Formata os dados da correção para exibição amigável.

    Parameters
    ----------
    correction_data : dict
        Dados da correção retornados por correct_english_text.

    Returns
    -------
    dict
        Dados formatados com chaves prontas para exibição.
    """
    if not correction_data:
        return {}

    return {
        "original": correction_data.get("original", ""),
        "texto_corrigido": correction_data.get("texto_corrigido", ""),
        "versao_natural": correction_data.get("versao_natural", ""),
        "explicacoes": correction_data.get("explicacoes", []),
        "phrasal_verbs": correction_data.get("phrasal_verbs", []),
        "expressoes_idiomaticas": correction_data.get("expressoes_idiomaticas", []),
        "novo_vocabulario": correction_data.get("novo_vocabulario", []),
    }


def get_correction_summary(correction_data):
    """
    Gera um resumo estatístico da correção.

    Parameters
    ----------
    correction_data : dict
        Dados da correção.

    Returns
    -------
    dict
        Dicionário com contagens de cada seção.
    """
    if not correction_data:
        return {
            "explicacoes": 0,
            "phrasal_verbs": 0,
            "expressoes_idiomaticas": 0,
            "novo_vocabulario": 0,
        }

    return {
        "explicacoes": len(correction_data.get("explicacoes", [])),
        "phrasal_verbs": len(correction_data.get("phrasal_verbs", [])),
        "expressoes_idiomaticas": len(
            correction_data.get("expressoes_idiomaticas", [])
        ),
        "novo_vocabulario": len(correction_data.get("novo_vocabulario", [])),
    }
