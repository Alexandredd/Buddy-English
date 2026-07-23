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

    Usa um contador de chaves para lidar corretamente com JSON
    aninhado (nested objects), evitando truncamento causado por
    regex non-greedy que para no primeiro '}'.

    Parameters
    ----------
    text : str
        Texto que contém (ou deveria conter) um JSON.

    Returns
    -------
    str
        A substring que parece ser JSON.
    """
    text = text.strip()

    # Remove blocos markdown ```json ... ```
    markdown_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if markdown_match:
        inner = markdown_match.group(1).strip()
        # Procura JSON dentro do bloco markdown
        extracted = _extract_json_balanced(inner)
        if extracted:
            return extracted

    # Procura JSON diretamente no texto todo
    extracted = _extract_json_balanced(text)
    if extracted:
        return extracted

    # Fallback: substring entre primeiro { e último }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return text


def _extract_json_balanced(text):
    """
    Encontra o primeiro '{' e extrai até o '}' correspondente
    que balanceia, respeitando strings e escapes.
    Retorna a substring JSON ou string vazia se não encontrar.
    """
    start = text.find("{")
    if start == -1:
        return ""

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return ""


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
    if not json_str:
        return {}

    repaired = json_str

    # Remove vírgulas antes de } ou ]
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)

    # Substitui aspas simples por aspas duplas em JSON.
    # Estratégia segura: se não houver aspas duplas no texto,
    # podemos simplesmente substituir ' por " (seguro porque
    # não há conflito com aspas duplas).
    # Se houver aspas duplas, tentamos substituir apenas as
    # aspas simples que claramente delimitam chaves/valores.
    if "'" in repaired and '"' not in repaired:
        # Sem aspas duplas: troca todas as aspas simples com segurança
        repaired = repaired.replace("'", '"')
    elif "'" in repaired:
        # Com aspas duplas: substitui aspas simples que estão
        # fora de strings com aspas duplas usando parse manual
        repaired = _replace_single_quotes_in_json(repaired)

    try:
        return json.loads(repaired)
    except (json.JSONDecodeError, TypeError):
        return {}


def _replace_single_quotes_in_json(text):
    """
    Substitui aspas simples por aspas duplas em posições onde
    elas claramente delimitam chaves ou valores JSON.
    Mantém intactas aspas simples dentro de strings já delimitadas
    por aspas duplas (como "don't", "can't", etc.).
    """
    result = []
    in_double_string = False
    in_single_string = False
    escape = False

    for ch in text:
        if escape:
            escape = False
            result.append(ch)
            continue
        if ch == '\\':
            escape = True
            result.append(ch)
            continue
        if ch == '"' and not in_single_string:
            in_double_string = not in_double_string
            result.append(ch)
            continue
        if ch == "'" and not in_double_string:
            in_single_string = not in_single_string
            # Substitui aspas simples delimitadoras por duplas
            result.append('"')
            continue
        result.append(ch)

    return "".join(result)


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
    escaped_json = json.dumps(text_content, ensure_ascii=False)

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

# Regras locais de correção (fallback quando LanguageTool e OpenAI não estão disponíveis)
_LOCAL_CORRECTION_PATTERNS = [
    (r"\bi have (\d{1,2}) yea\b", r"I am \1 years old", "Ajuste de estrutura de idade (yea -> years old)."),
    (r"\bi have (\d{1,2}) year\b", r"I am \1 years old", "Ajuste de estrutura de idade (year -> years old)."),
    (r"\bi have (\d{1,2}) years\b", r"I am \1 years old", "Ajuste de estrutura de idade."),
    (r"\bi have (\d{1,2}) years old\b", r"I am \1 years old", "Ajuste de estrutura de idade."),
    (r"\bhow is your name\b", "what is your name", "Ajuste de pergunta natural."),
    (r"\bmy name is ([a-z]+) and i have (\d{1,2}) years\b", r"My name is \1 and I am \2 years old", "Ajuste de estrutura natural."),
    (r"\bi am with (doubt|doubts)\b", "I have a question", "Ajuste de expressao natural."),
    (r"\bi have sure\b", "I am sure", "Ajuste de expressao natural."),
    (r"\bmore better\b", "better", "Ajuste de comparativo."),
    (r"\bmore easier\b", "easier", "Ajuste de comparativo."),
    (r"\bmore faster\b", "faster", "Ajuste de comparativo."),
    (r"\btake easy\b", "take it easy", "Ajuste de expressao natural."),
    (r"\btake it easy man\b", "take it easy, man", "Ajuste de pontuacao vocativa."),
    (r"\bin the weekend\b", "on the weekend", "Ajuste para uso comum no ingles americano."),
    (r"\bmake a party\b", "have a party", "Ajuste de colocacao comum."),
    (r"\bdo a party\b", "have a party", "Ajuste de colocacao comum."),
    (r"\bmarried with\b", "married to", "Ajuste de preposicao."),
    (r"\bdepend of\b", "depend on", "Ajuste de preposicao."),
    (r"\bdiscuss about\b", "discuss", "Ajuste de verbo sem preposicao."),
    (r"\bexplain me\b", "explain to me", "Ajuste de preposicao."),
    (r"\bi have a doubt\b", "I have a question", "Ajuste de expressao natural."),
    (r"\bif i was\b", "if I were", "Ajuste de modo verbal."),
    (r"\bpeople is\b", "people are", "Ajuste de concordancia."),
    (r"\binformations\b", "information", "Ajuste de substantivo incontavel."),
    (r"\badvices\b", "advice", "Ajuste de substantivo incontavel."),
    (r"\bfurnitures\b", "furniture", "Ajuste de substantivo incontavel."),
    (r"\bhome office\b", "remote work", "Ajuste de termo mais natural em ingles americano."),
    (r"\bopen the camera\b", "turn on the camera", "Ajuste de verbo frasal."),
    (r"\bclose the camera\b", "turn off the camera", "Ajuste de verbo frasal."),
    (r"\bturn on the light\b", "turn on the lights", "Ajuste de uso comum."),
    (r"\bi\b", "I", "Pronome pessoal em maiusculo."),
    (r"\bdont\b", "don't", "Correcao ortografica."),
    (r"\bcant\b", "can't", "Correcao ortografica."),
    (r"\bdoesnt\b", "doesn't", "Correcao ortografica."),
    (r"\bdidnt\b", "didn't", "Correcao ortografica."),
    (r"\bwont\b", "won't", "Correcao ortografica."),
    (r"\bshouldnt\b", "shouldn't", "Correcao ortografica."),
    (r"\bcouldnt\b", "couldn't", "Correcao ortografica."),
    (r"\bim\b", "I'm", "Correcao de contracao."),
    (r"\bive\b", "I've", "Correcao de contracao."),
    (r"\bill\b", "I'll", "Correcao de contracao."),
    (r"\bid\b", "I'd", "Correcao de contracao."),
    (r"\bweve\b", "we've", "Correcao de contracao."),
    (r"\btheyre\b", "they're", "Correcao de contracao."),
    (r"\byoure\b", "you're", "Correcao de contracao."),
    (r"\bits\b", "it's", "Correcao de contracao."),
    (r"\bteh\b", "the", "Correcao ortografica."),
    (r"\brecieve\b", "receive", "Correcao ortografica."),
    (r"\badress\b", "address", "Correcao ortografica."),
    (r"\bwich\b", "which", "Correcao ortografica."),
    (r"\bsepareted\b", "separated", "Correcao ortografica."),
    (r"\bdefinately\b", "definitely", "Correcao ortografica."),
    (r"\boccured\b", "occurred", "Correcao ortografica."),
    (r"\bhe go\b", "he goes", "Ajuste de concordancia verbal."),
    (r"\bshe go\b", "she goes", "Ajuste de concordancia verbal."),
    (r"\bit go\b", "it goes", "Ajuste de concordancia verbal."),
    (r"\bhe have\b", "he has", "Ajuste de concordancia verbal."),
    (r"\bshe have\b", "she has", "Ajuste de concordancia verbal."),
    (r"\bit have\b", "it has", "Ajuste de concordancia verbal."),
    (r"\bthere is many\b", "there are many", "Ajuste de concordancia."),
    (r"\bthere is a lot of people\b", "there are a lot of people", "Ajuste de concordancia."),
    (r"\bone of the bests\b", "one of the best", "Ajuste de pluralizacao."),
    (r"\btakw\b", "take", "Correcao ortografica."),
]


def _apply_local_corrections(text):
    """
    Aplica correções locais offline (regras de regex) ao texto.

    Parameters
    ----------
    text : str
        Texto em inglês a ser corrigido.

    Returns
    -------
    tuple
        (texto_corrigido, lista_de_ajustes)
    """
    import re as _re

    original = text or ""
    corrigido = original
    ajustes = []

    if not original.strip():
        return original, ajustes

    # Normaliza espaços duplicados e espaços antes de pontuação
    novo = _re.sub(r"\s+", " ", corrigido).strip()
    novo = _re.sub(r"\s+([,.;:!?])", r"\1", novo)
    if novo != corrigido:
        ajustes.append({"mensagem": "Ajuste de espacos.", "de": corrigido, "para": novo})
        corrigido = novo

    for pattern, replacement, mensagem in _LOCAL_CORRECTION_PATTERNS:
        novo = _re.sub(pattern, replacement, corrigido, flags=_re.IGNORECASE)
        if novo != corrigido:
            ajustes.append({"mensagem": mensagem, "de": corrigido, "para": novo})
            corrigido = novo

    # Capitaliza início de sentenças
    partes = _re.split(r"([.!?]\s+)", corrigido)
    partes_corrigidas = []
    for i, parte in enumerate(partes):
        if i % 2 == 0:
            stripped = parte.lstrip()
            if stripped:
                prefix = parte[: len(parte) - len(stripped)]
                parte = prefix + stripped[0].upper() + stripped[1:]
        partes_corrigidas.append(parte)
    novo = "".join(partes_corrigidas)
    if novo != corrigido:
        ajustes.append({"mensagem": "Capitalizacao de sentencas.", "de": corrigido, "para": novo})
        corrigido = novo

    if corrigido and corrigido[-1] not in ".!?":
        novo = f"{corrigido}."
        ajustes.append({"mensagem": "Pontuacao final.", "de": corrigido, "para": novo})
        corrigido = novo

    return corrigido, ajustes


def _try_get_app_correction_functions():
    """
    Tenta obter as funções corrigir_texto e correcao_local_basica do módulo app.

    No Streamlit Cloud, o app pode estar carregado como '__main__' ou 'streamlit_app',
    então verificamos sys.modules com vários nomes possíveis.

    Returns
    -------
    tuple
        (corrigir_texto, correcao_local_basica) - podem ser None se não encontrados.
    """
    import sys

    for module_name in ("app", "__main__", "streamlit_app"):
        module = sys.modules.get(module_name)
        if module is None:
            continue
        corrigir_texto = getattr(module, "corrigir_texto", None)
        correcao_local_basica = getattr(module, "correcao_local_basica", None)
        if corrigir_texto or correcao_local_basica:
            return corrigir_texto, correcao_local_basica

    return None, None


def correct_english_text_fallback(text):
    """
    Correção básica sem IA (usando LanguageTool + correções locais).

    Esta função é usada como fallback quando a API OpenAI não está disponível.
    Primeiro tenta usar as funções do app.py (via sys.modules), e se não conseguir,
    usa as regras locais embutidas neste módulo. SEMPRE aplica as correções
    locais como passo final para garantir consistência.

    Parameters
    ----------
    text : str
        Texto em inglês a ser corrigido.

    Returns
    -------
    dict
        Dados da correção no mesmo formato do módulo de IA.
    """
    texto_corrigido = text
    ajustes = []

    # Tenta obter as funções do app.py via sys.modules
    corrigir_texto, _ = _try_get_app_correction_functions()

    # Correção com LanguageTool (se disponível via app.py)
    if corrigir_texto:
        try:
            result = corrigir_texto(text)
            texto_corrigido = result.get("texto_corrigido", text)
            ajustes = result.get("ajustes", [])
        except Exception:
            pass

    # SEMPRE aplica as correções locais embutidas neste módulo como passo final.
    # Isso garante que padrões como "I have 52 year" sejam corrigidos,
    # independentemente do que a função do app.py tenha aplicado.
    texto_corrigido, ajustes_locais = _apply_local_corrections(texto_corrigido)
    ajustes.extend(ajustes_locais)

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
