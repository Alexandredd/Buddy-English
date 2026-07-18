import streamlit as st
import requests
import difflib
import random
import re
import os
import hashlib
import json
import html
from pathlib import Path
from gtts import gTTS
import base64
from io import BytesIO
from datetime import datetime, timezone
import importlib
import daily_phrases as dp
import public_domain_texts as pdt
import news_podcast as npc
import chuncks as ck

try:
    _deep_translator = importlib.import_module("deep_translator")
    GoogleTranslator = _deep_translator.GoogleTranslator
except Exception:
    GoogleTranslator = None

try:
    _pydub = importlib.import_module("pydub")
    AudioSegment = _pydub.AudioSegment
except Exception:
    AudioSegment = None


dp = importlib.reload(dp)
pdt = importlib.reload(pdt)
npc = importlib.reload(npc)
ck = importlib.reload(ck)


MANUAL_READING_TEXTS_FILE = Path(__file__).with_name("reading_manual_texts.json")
FAVORITE_PHRASES_FILE = Path(__file__).with_name("favorite_phrases.json")


def load_manual_reading_texts():
    if not MANUAL_READING_TEXTS_FILE.exists():
        return []
    try:
        with MANUAL_READING_TEXTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    valid = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        text = str(item.get("text", "")).strip()
        updated_at = str(item.get("updated_at", "")).strip()
        if title and text:
            valid.append({"title": title, "text": text, "updated_at": updated_at})
    return valid


def save_manual_reading_texts(items):
    with MANUAL_READING_TEXTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)


def load_favorite_phrases():
    if not FAVORITE_PHRASES_FILE.exists():
        return set()
    try:
        with FAVORITE_PHRASES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return set()

    if not isinstance(data, list):
        return set()

    valid = set()
    for item in data:
        text = str(item).strip()
        if "::" in text:
            valid.add(text)
    return valid


def save_favorite_phrases(items):
    payload = sorted(str(item) for item in items if isinstance(item, str) and "::" in item)
    with FAVORITE_PHRASES_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _fallback_list_contexts():
    return []


def _fallback_filter_phrases(context):
    return []


def _fallback_suggest_new_phrases(context, limit=3):
    return []


def _fallback_save_extra_phrase(phrase):
    return False


def _fallback_parse_phrases_json(content):
    return []


def _fallback_parse_phrases_csv(content):
    return []


def _fallback_save_extra_phrases_bulk(phrases):
    return {"added": 0, "duplicates": 0, "invalid": len(phrases) if phrases else 0}


def _fallback_export_all_phrases_json():
    return "[]"


def _fallback_export_all_phrases_csv():
    return "context,english,when_to_use,best_translation\n"


def _fallback_fetch_online_phrases(limit=3, force_refresh=False):
    return []


def _fallback_get_online_cache_info():
    return {"status": "Sem cache", "updated_at": "-", "count": "0"}


def _fallback_get_last_auto_update_date():
    return ""


def _fallback_set_last_auto_update_date(date_iso):
    return None


def _fallback_get_all_phrases():
    return []


def decode_uploaded_text(raw_bytes):
    """Decodifica bytes de upload com fallbacks comuns para evitar erro de Unicode."""
    if raw_bytes is None:
        return ""

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("utf-8", errors="replace")


def _fallback_list_public_titles():
    return []


def _fallback_get_public_text_by_title(title):
    return {
        "title": "Sem textos",
        "author": "-",
        "year": "-",
        "source": "-",
        "text": "",
    }


def _fallback_split_paragraphs(text):
    return []


def _fallback_get_last_public_text_update_date():
    return ""


def _fallback_set_last_public_text_update_date(date_iso):
    return None


def _fallback_incorporate_daily_public_texts(limit=1):
    return 0


def _fallback_fetch_and_incorporate_online_public_texts(limit=1):
    return 0


def _fallback_get_last_online_public_text_fetch_status():
    return {"updated_at": "", "status": "", "details": ""}


list_contexts = getattr(dp, "list_contexts", _fallback_list_contexts)
filter_phrases = getattr(dp, "filter_phrases", _fallback_filter_phrases)
suggest_new_phrases = getattr(dp, "suggest_new_phrases", _fallback_suggest_new_phrases)
save_extra_phrase = getattr(dp, "save_extra_phrase", _fallback_save_extra_phrase)
parse_phrases_json = getattr(dp, "parse_phrases_json", _fallback_parse_phrases_json)
parse_phrases_csv = getattr(dp, "parse_phrases_csv", _fallback_parse_phrases_csv)
save_extra_phrases_bulk = getattr(dp, "save_extra_phrases_bulk", _fallback_save_extra_phrases_bulk)
export_all_phrases_json = getattr(dp, "export_all_phrases_json", _fallback_export_all_phrases_json)
export_all_phrases_csv = getattr(dp, "export_all_phrases_csv", _fallback_export_all_phrases_csv)
fetch_online_phrases = getattr(dp, "fetch_online_phrases", _fallback_fetch_online_phrases)
get_online_cache_info = getattr(dp, "get_online_cache_info", _fallback_get_online_cache_info)
get_last_auto_update_date = getattr(dp, "get_last_auto_update_date", _fallback_get_last_auto_update_date)
set_last_auto_update_date = getattr(dp, "set_last_auto_update_date", _fallback_set_last_auto_update_date)
get_all_phrases = getattr(dp, "get_all_phrases", _fallback_get_all_phrases)

list_public_titles = getattr(pdt, "list_public_titles", _fallback_list_public_titles)
get_public_text_by_title = getattr(pdt, "get_public_text_by_title", _fallback_get_public_text_by_title)
split_public_paragraphs = getattr(pdt, "split_paragraphs", _fallback_split_paragraphs)
get_last_public_text_update_date = getattr(
    pdt,
    "get_last_auto_update_date",
    _fallback_get_last_public_text_update_date,
)
set_last_public_text_update_date = getattr(
    pdt,
    "set_last_auto_update_date",
    _fallback_set_last_public_text_update_date,
)
incorporate_daily_public_texts = getattr(
    pdt,
    "incorporate_daily_public_texts",
    _fallback_incorporate_daily_public_texts,
)
fetch_and_incorporate_online_public_texts = getattr(
    pdt,
    "fetch_and_incorporate_online_public_texts",
    _fallback_fetch_and_incorporate_online_public_texts,
)
get_last_online_public_text_fetch_status = getattr(
    pdt,
    "get_last_online_fetch_status",
    _fallback_get_last_online_public_text_fetch_status,
)

st.set_page_config(page_title="English Buddy", page_icon="📘")
st.title("English Buddy - Treine seu Inglês")

if "favorite_phrases" not in st.session_state:
    st.session_state.favorite_phrases = load_favorite_phrases()

if "reading_translation_cache" not in st.session_state:
    st.session_state.reading_translation_cache = {}

if "reading_manual_input" not in st.session_state:
    st.session_state.reading_manual_input = ""

if "reading_manual_title" not in st.session_state:
    st.session_state.reading_manual_title = "Meu texto"

if "reading_manual_selected" not in st.session_state:
    st.session_state.reading_manual_selected = ""

if "podcast_news_items" not in st.session_state:
    st.session_state.podcast_news_items = []

if "podcast_translation_cache" not in st.session_state:
    st.session_state.podcast_translation_cache = {}

if "chunks_initialized" not in st.session_state:
    st.session_state.chunks_initialized = True
    st.session_state.chunks_stats = ck.get_study_statistics()

# --- Menu lateral ---
menu = st.sidebar.radio("Escolha uma habilidade:", [
    "Escuta 🎧", "Tradução 🌍", "Dicionário 🇺🇸", "Conjugação 🔄", "Leitura 📖", "Frases do dia a dia 💬",
    "Podcast de Notícias 🎙️", "Chunks de Estudo 📚"
])

# --- Função de correção ---
LANGUAGETOOL_ENDPOINTS = [
    "https://api.languagetool.org/v2/check",
    "https://languagetool.org/api/v2/check",
]


def _consultar_languagetool(texto):
    data = {
        "text": texto,
        "language": "en-US",
        "preferredVariants": "en-US",
        "enabledOnly": "false",
    }

    ultimo_erro = None
    for endpoint in LANGUAGETOOL_ENDPOINTS:
        try:
            response = requests.post(endpoint, data=data, timeout=20)
            response.raise_for_status()
            return response.json(), endpoint
        except requests.RequestException as exc:
            ultimo_erro = exc

    if ultimo_erro:
        raise ultimo_erro
    raise requests.RequestException("Falha ao consultar servicos de correcao.")


def corrigir_texto(texto):
    """Corrige texto completo com LanguageTool em variante americana."""
    texto_original = texto or ""
    if not texto_original.strip():
        return {"texto_corrigido": texto_original, "ajustes": [], "endpoint_usado": ""}

    endpoint_usado = ""
    texto_corrigido = texto_original
    ajustes = []
    try:
        result, endpoint_usado = _consultar_languagetool(texto_original)
        matches = sorted(result.get("matches", []), key=lambda item: item.get("offset", 0), reverse=True)
        intervalos_aplicados = []

        for match in matches:
            offset = int(match.get("offset", 0))
            length = int(match.get("length", 0))
            fim = offset + length
            replacements = match.get("replacements", [])

            if any(not (fim <= ini or offset >= fim_existente) for ini, fim_existente in intervalos_aplicados):
                continue
            if not replacements:
                continue

            sugestao = replacements[0].get("value", "")
            trecho_original = texto_original[offset:fim]
            if trecho_original == sugestao:
                continue

            # Ignora ajustes de espaco sem impacto semantico (ex.: "  " -> " ").
            if trecho_original.strip() == "" and sugestao.strip() == "":
                continue

            texto_corrigido = texto_corrigido[:offset] + sugestao + texto_corrigido[fim:]
            intervalos_aplicados.append((offset, fim))
            ajustes.append(
                {
                    "mensagem": match.get("message", "Ajuste sugerido."),
                    "de": trecho_original,
                    "para": sugestao,
                }
            )
        ajustes.reverse()
    except requests.RequestException:
        endpoint_usado = "local"

    # Segunda camada local para corrigir construcoes frequentes (ex.: "I have 52 years").
    texto_corrigido_local, ajustes_locais = correcao_local_basica(texto_corrigido)
    if texto_corrigido_local != texto_corrigido:
        texto_corrigido = texto_corrigido_local
    ajustes.extend(ajustes_locais)

    return {
        "texto_corrigido": texto_corrigido,
        "ajustes": ajustes,
        "endpoint_usado": endpoint_usado,
    }


def correcao_local_basica(texto):
    """Aplica correcao local offline para casos sem conectividade externa."""
    original = texto or ""
    corrigido = original
    ajustes = []

    if not original.strip():
        return original, ajustes

    # Normaliza espacos duplicados e espacos antes de pontuacao.
    novo = re.sub(r"\s+", " ", corrigido).strip()
    novo = re.sub(r"\s+([,.;:!?])", r"\1", novo)
    if novo != corrigido:
        ajustes.append({"mensagem": "Ajuste de espacos.", "de": corrigido, "para": novo})
        corrigido = novo

    padroes = [
        (r"\btakw\b", "take", "Correcao ortografica."),
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
    ]

    for pattern, replacement, mensagem in padroes:
        novo = re.sub(pattern, replacement, corrigido, flags=re.IGNORECASE)
        if novo != corrigido:
            ajustes.append({"mensagem": mensagem, "de": corrigido, "para": novo})
            corrigido = novo

    # Capitaliza inicio de sentencas.
    partes = re.split(r"([.!?]\s+)", corrigido)
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


def formatar_trecho_ajuste(valor):
    texto = str(valor or "")
    if texto == "":
        return "(vazio)"
    if texto.isspace():
        return f"(espacos x{len(texto)})"
    return texto.replace("\n", "\\n").replace("\t", "\\t")


def refinar_texto_americano_ia(texto, api_key, model="gpt-4o-mini", nivel="Nativo US"):
    """Refina texto para ingles americano conforme nivel escolhido."""
    if not api_key:
        return texto

    instrucoes_por_nivel = {
        "Basico": (
            "Correct only clear grammar, spelling, punctuation, and agreement mistakes in US English. "
            "Keep sentence structure as close as possible to the original."
        ),
        "Estrito": (
            "Correct grammar, spelling, punctuation, agreement, syntax, and clarity in US English. "
            "You may reorder parts for correctness and clarity, while preserving meaning and tone."
        ),
        "Nativo US": (
            "Rewrite and correct the full text in natural US English, fixing grammar, spelling, punctuation, agreement, syntax, and word choice. "
            "Improve flow to sound native while preserving original meaning and tone."
        ),
    }
    instrucoes_nivel = instrucoes_por_nivel.get(nivel, instrucoes_por_nivel["Nativo US"])

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert American English editor. "
                f"{instrucoes_nivel} "
                "Preserve original meaning and tone. "
                "Do not add new information. "
                "Return only the corrected text."
            ),
        },
        {"role": "user", "content": texto},
    ]

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.1,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip() or texto
    except requests.RequestException:
        return texto

# --- Função de áudio ---
def _montar_audio_continuo(tts):
    """Concatena os trechos de audio do gTTS em um unico stream continuo.

    Textos longos fazem o gTTS realizar varias chamadas a API, cada uma
    gerando um mp3 independente. Concatenar esses trechos em bytes crus
    (comportamento padrao do gTTS) costuma causar cliques/picotes entre os
    trechos. Para evitar isso, decodificamos cada trecho com o pydub e
    remontamos um unico audio continuo antes de exportar.
    """
    if AudioSegment is None:
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()

    try:
        combinado = AudioSegment.empty()
        for parte in tts.stream():
            combinado += AudioSegment.from_file(BytesIO(parte), format="mp3")
        buffer = BytesIO()
        combinado.export(buffer, format="mp3")
        buffer.seek(0)
        return buffer.read()
    except Exception:
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()


def gerar_audio(frase, playback_rate=1.0):
    tts = gTTS(frase, lang="en")
    audio_base64 = base64.b64encode(_montar_audio_continuo(tts)).decode()
    audio_id = f"audio_{abs(hash(frase)) % 10_000_000}"
    audio_html = f"""
        <audio id="{audio_id}" controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Seu navegador não suporta áudio.
        </audio>
        <script>
            (function() {{
                const el = document.getElementById("{audio_id}");
                if (el) {{
                    el.playbackRate = {playback_rate};
                }}
            }})();
        </script>
    """
    return audio_html


def gerar_audio_ingles_sotaque(frase, sotaque="Americano (EUA)", playback_rate=1.0):
    """Gera audio em ingles com sotaque/regiao selecionada, com fallback seguro."""
    mapa_tld = {
        "Americano (EUA)": "com",
        "Britânico (Reino Unido)": "co.uk",
        "Global (Neutro)": "com",
        "Indiano": "co.in",
        "Australiano": "com.au",
        "Irlandês": "ie",
        "Sul-africano": "co.za",
        "Nigeriano": "com.ng",
        "Asiático (Hong Kong)": "com.hk",
    }
    tld = mapa_tld.get(sotaque, "com")

    try:
        tts = gTTS(frase, lang="en", tld=tld)
    except Exception:
        tts = gTTS(frase, lang="en")

    audio_base64 = base64.b64encode(_montar_audio_continuo(tts)).decode()
    audio_id = f"audio_accent_{abs(hash(frase + sotaque)) % 10_000_000}"
    audio_html = f"""
        <audio id="{audio_id}" controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Seu navegador não suporta áudio.
        </audio>
        <script>
            (function() {{
                const el = document.getElementById("{audio_id}");
                if (el) {{
                    el.playbackRate = {playback_rate};
                }}
            }})();
        </script>
    """
    return audio_html

# --- Função de tradução ---
def _chunk_text_for_translation(texto, max_chars=380):
    """Divide textos longos em blocos menores para respeitar limite da API."""
    text = (texto or "").strip()
    if not text:
        return []

    chunks = []
    current = ""

    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            candidate = f"{current}\n" if current else ""
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = ""
            continue

        candidate = f"{current}\n{line}" if current else line
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(line) <= max_chars:
            current = line
            continue

        words = line.split(" ")
        sub_current = ""
        for word in words:
            sub_candidate = f"{sub_current} {word}".strip()
            if len(sub_candidate) <= max_chars:
                sub_current = sub_candidate
            else:
                if sub_current:
                    chunks.append(sub_current)
                if len(word) > max_chars:
                    for i in range(0, len(word), max_chars):
                        chunks.append(word[i : i + max_chars])
                    sub_current = ""
                else:
                    sub_current = word
        if sub_current:
            current = sub_current

    if current:
        chunks.append(current)

    return chunks


def _normalize_translation_text(texto):
    return re.sub(r"\s+", " ", (texto or "").strip()).casefold()


def _should_try_translation_fallback(original, translated, origem, destino):
    if origem == destino:
        return False
    if not (original or "").strip() or not (translated or "").strip():
        return False
    if _normalize_translation_text(original) != _normalize_translation_text(translated):
        return False

    # Evita fallback para entradas sem letras (numeros/simbolos) ou muito longas.
    if not re.search(r"[A-Za-zÀ-ÿ]", original):
        return False
    if len(original.strip()) > 120:
        return False
    return True


def _translate_text_fallback(original, origem, destino):
    if GoogleTranslator is None:
        translated = ""
    else:
        try:
            translated = GoogleTranslator(source=origem, target=destino).translate(original)
            translated = (translated or "").strip()
            if translated:
                return translated
        except Exception:
            translated = ""

    # Fallback HTTP sem dependencia externa.
    try:
        response = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": origem,
                "tl": destino,
                "dt": "t",
                "q": original,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list) and payload and isinstance(payload[0], list):
            parts = []
            for item in payload[0]:
                if isinstance(item, list) and item:
                    parts.append(str(item[0]))
            return "".join(parts).strip()
    except Exception:
        return ""

    return ""


def traduzir_texto(texto, origem="pt", destino="en", progress_callback=None):
    url = "https://api.mymemory.translated.net/get"
    partes = _chunk_text_for_translation(texto)
    if not partes:
        return ""

    traducao_partes = []
    total_partes = len(partes)
    for indice, parte in enumerate(partes, start=1):
        params = {"q": parte, "langpair": f"{origem}|{destino}"}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        result = response.json()
        translated = result.get("responseData", {}).get("translatedText", "")
        translated = html.unescape(translated)
        if _should_try_translation_fallback(parte, translated, origem, destino):
            fallback = _translate_text_fallback(parte, origem, destino)
            if fallback:
                translated = fallback
        if not translated:
            detail = result.get("responseDetails", "")
            raise ValueError(detail or "Tradução indisponível no momento.")
        traducao_partes.append(translated)
        if progress_callback:
            progress_callback(indice, total_partes)

    return "\n".join(traducao_partes)


def traduzir_texto_google(texto, origem="pt", destino="en", progress_callback=None):
    """Traduz texto usando Google Translator (biblioteca ou endpoint HTTP)."""
    partes = _chunk_text_for_translation(texto)
    if not partes:
        return ""

    traducao_partes = []
    total_partes = len(partes)
    for indice, parte in enumerate(partes, start=1):
        translated = _translate_text_fallback(parte, origem, destino)
        if not translated:
            raise ValueError("Tradução indisponível no momento.")
        traducao_partes.append(translated)
        if progress_callback:
            progress_callback(indice, total_partes)

    return "\n".join(traducao_partes)


def _merriam_audio_subdir(audio_code):
    code = (audio_code or "").strip().lower()
    if not code:
        return ""
    if code.startswith("bix"):
        return "bix"
    if code.startswith("gg"):
        return "gg"
    if not code[0].isalpha():
        return "number"
    return code[0]


def _buscar_dicionario_merriam_webster(termo, api_key):
    palavra = (termo or "").strip()
    if not palavra or not api_key:
        return None

    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{palavra}"
    response = requests.get(url, params={"key": api_key}, timeout=20)
    response.raise_for_status()
    payload = response.json()

    if isinstance(payload, list) and payload and isinstance(payload[0], str):
        sugestoes = [s for s in payload[:8] if isinstance(s, str)]
        return {"found": False, "word": palavra, "suggestions": sugestoes, "source": "Merriam-Webster"}

    entries = [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []
    if not entries:
        return {"found": False, "word": palavra, "source": "Merriam-Webster"}

    entry = entries[0]
    hwi = entry.get("hwi", {}) if isinstance(entry, dict) else {}
    prs = hwi.get("prs", []) if isinstance(hwi, dict) else []
    phonetic_text = ""
    audio_url = ""
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        mw = (pr.get("mw") or "").strip()
        sound = pr.get("sound", {}) if isinstance(pr.get("sound", {}), dict) else {}
        audio_code = (sound.get("audio") or "").strip()
        if not phonetic_text and mw:
            phonetic_text = f"/{mw}/"
        if not audio_url and audio_code:
            subdir = _merriam_audio_subdir(audio_code)
            if subdir:
                audio_url = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio_code}.mp3"
        if phonetic_text and audio_url:
            break

    fl = (entry.get("fl") or "-").strip()
    shortdef = entry.get("shortdef", []) if isinstance(entry.get("shortdef", []), list) else []
    defs = [{"definition": str(d).strip(), "example": ""} for d in shortdef[:6] if str(d).strip()]

    syns = []
    meta = entry.get("meta", {}) if isinstance(entry.get("meta", {}), dict) else {}
    raw_syns = meta.get("syns", []) if isinstance(meta.get("syns", []), list) else []
    for group in raw_syns:
        if isinstance(group, list):
            for item in group:
                if isinstance(item, str) and item.strip():
                    syns.append(item.strip())

    meanings = []
    if defs:
        meanings.append(
            {
                "part_of_speech": fl,
                "definitions": defs,
                "synonyms": syns[:12],
            }
        )

    return {
        "found": bool(meanings),
        "word": (entry.get("meta", {}).get("id", palavra).split(":")[0]).strip(),
        "phonetic": phonetic_text,
        "audio_url": audio_url,
        "meanings": meanings,
        "source": "Merriam-Webster",
    }


def _buscar_dicionario_publico(termo):
    palavra = (termo or "").strip()
    if not palavra:
        return None

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{palavra}"
    response = requests.get(url, timeout=20)
    if response.status_code == 404:
        return {"found": False, "word": palavra}

    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or not payload:
        return {"found": False, "word": palavra}

    entry = payload[0]
    phonetics = entry.get("phonetics", []) if isinstance(entry, dict) else []
    meanings = entry.get("meanings", []) if isinstance(entry, dict) else []

    phonetic_text = ""
    audio_url = ""
    for item in phonetics:
        if not isinstance(item, dict):
            continue
        text = (item.get("text") or "").strip()
        audio = (item.get("audio") or "").strip()
        if not phonetic_text and text:
            phonetic_text = text
        if not audio_url and audio:
            audio_url = audio
        if phonetic_text and audio_url:
            break

    parsed_meanings = []
    for meaning in meanings:
        if not isinstance(meaning, dict):
            continue
        part_of_speech = (meaning.get("partOfSpeech") or "-").strip()
        defs = meaning.get("definitions", [])
        synonyms = [s for s in (meaning.get("synonyms") or []) if isinstance(s, str) and s.strip()]
        parsed_defs = []
        for d in defs[:4]:
            if not isinstance(d, dict):
                continue
            definition = (d.get("definition") or "").strip()
            example = (d.get("example") or "").strip()
            if definition:
                parsed_defs.append({"definition": definition, "example": example})
        if parsed_defs:
            parsed_meanings.append(
                {
                    "part_of_speech": part_of_speech,
                    "definitions": parsed_defs,
                    "synonyms": synonyms[:12],
                }
            )

    return {
        "found": True,
        "word": (entry.get("word") or palavra).strip(),
        "phonetic": phonetic_text,
        "audio_url": audio_url,
        "meanings": parsed_meanings,
        "source": "Free Dictionary API",
    }


def buscar_dicionario_ingles(termo, merriam_api_key=""):
    """Consulta dicionario EN-EN priorizando Merriam-Webster com fallback publico."""
    key = (merriam_api_key or "").strip()
    if key:
        try:
            result = _buscar_dicionario_merriam_webster(termo, key)
            if result is not None:
                return result
        except requests.RequestException:
            pass

    try:
        return _buscar_dicionario_publico(termo)
    except requests.RequestException:
        palavra = (termo or "").strip()
        return {"found": False, "word": palavra}


def incorporar_frases_online(frases_online):
    """Traduz e salva frases online novas, retornando quantidade adicionada."""
    adicionadas_online = 0
    for frase_online in frases_online:
        if not frase_online.get("best_translation"):
            try:
                frase_online["best_translation"] = traduzir_texto(
                    frase_online["english"], origem="en", destino="pt"
                )
            except Exception:
                frase_online["best_translation"] = "Tradução indisponível no momento."
        if save_extra_phrase(frase_online):
            adicionadas_online += 1
    return adicionadas_online


def build_inline_diff(original: str, corrected: str) -> str:
    """Gera diff inline robusto em nivel de caracteres (sem duplicar tokens)."""
    matcher = difflib.SequenceMatcher(None, original or "", corrected or "")
    parts = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_chunk = html.escape((original or "")[i1:i2])
        new_chunk = html.escape((corrected or "")[j1:j2])

        if tag == "equal":
            parts.append(new_chunk)
        elif tag == "delete":
            parts.append(f"<span style='color:#b00020;text-decoration:line-through'>{old_chunk}</span>")
        elif tag == "insert":
            parts.append(f"<span style='color:#0b8043;font-weight:600'>{new_chunk}</span>")
        elif tag == "replace":
            if old_chunk:
                parts.append(f"<span style='color:#b00020;text-decoration:line-through'>{old_chunk}</span>")
            if new_chunk:
                parts.append(f"<span style='color:#0b8043;font-weight:600'>{new_chunk}</span>")

    return "".join(parts)

# --- Conjugação manual de 50 verbos irregulares ---
conjugacoes = {
    "be": {"Present": "am / is / are", "Past": "was / were", "Past Participle": "been", "Gerund": "being"},
    "become": {"Present": "become / becomes", "Past": "became", "Past Participle": "become", "Gerund": "becoming"},
    "begin": {"Present": "begin / begins", "Past": "began", "Past Participle": "begun", "Gerund": "beginning"},
    "break": {"Present": "break / breaks", "Past": "broke", "Past Participle": "broken", "Gerund": "breaking"},
    "bring": {"Present": "bring / brings", "Past": "brought", "Past Participle": "brought", "Gerund": "bringing"},
    "build": {"Present": "build / builds", "Past": "built", "Past Participle": "built", "Gerund": "building"},
    "buy": {"Present": "buy / buys", "Past": "bought", "Past Participle": "bought", "Gerund": "buying"},
    "catch": {"Present": "catch / catches", "Past": "caught", "Past Participle": "caught", "Gerund": "catching"},
    "choose": {"Present": "choose / chooses", "Past": "chose", "Past Participle": "chosen", "Gerund": "choosing"},
    "come": {"Present": "come / comes", "Past": "came", "Past Participle": "come", "Gerund": "coming"},
    "cost": {"Present": "cost / costs", "Past": "cost", "Past Participle": "cost", "Gerund": "costing"},
    "cut": {"Present": "cut / cuts", "Past": "cut", "Past Participle": "cut", "Gerund": "cutting"},
    "do": {"Present": "do / does", "Past": "did", "Past Participle": "done", "Gerund": "doing"},
    "draw": {"Present": "draw / draws", "Past": "drew", "Past Participle": "drawn", "Gerund": "drawing"},
    "drink": {"Present": "drink / drinks", "Past": "drank", "Past Participle": "drunk", "Gerund": "drinking"},
    "drive": {"Present": "drive / drives", "Past": "drove", "Past Participle": "driven", "Gerund": "driving"},
    "eat": {"Present": "eat / eats", "Past": "ate", "Past Participle": "eaten", "Gerund": "eating"},
    "fall": {"Present": "fall / falls", "Past": "fell", "Past Participle": "fallen", "Gerund": "falling"},
    "feel": {"Present": "feel / feels", "Past": "felt", "Past Participle": "felt", "Gerund": "feeling"},
    "find": {"Present": "find / finds", "Past": "found", "Past Participle": "found", "Gerund": "finding"},
    "fly": {"Present": "fly / flies", "Past": "flew", "Past Participle": "flown", "Gerund": "flying"},
    "forget": {"Present": "forget / forgets", "Past": "forgot", "Past Participle": "forgotten", "Gerund": "forgetting"},
    "get": {"Present": "get / gets", "Past": "got", "Past Participle": "got / gotten", "Gerund": "getting"},
    "give": {"Present": "give / gives", "Past": "gave", "Past Participle": "given", "Gerund": "giving"},
    "go": {"Present": "go / goes", "Past": "went", "Past Participle": "gone", "Gerund": "going"},
    "grow": {"Present": "grow / grows", "Past": "grew", "Past Participle": "grown", "Gerund": "growing"},
    "have": {"Present": "have / has", "Past": "had", "Past Participle": "had", "Gerund": "having"},
    "hear": {"Present": "hear / hears", "Past": "heard", "Past Participle": "heard", "Gerund": "hearing"},
    "hold": {"Present": "hold / holds", "Past": "held", "Past Participle": "held", "Gerund": "holding"},
    "keep": {"Present": "keep / keeps", "Past": "kept", "Past Participle": "kept", "Gerund": "keeping"},
    "know": {"Present": "know / knows", "Past": "knew", "Past Participle": "known", "Gerund": "knowing"},
    "leave": {"Present": "leave / leaves", "Past": "left", "Past Participle": "left", "Gerund": "leaving"},
    "lose": {"Present": "lose / loses", "Past": "lost", "Past Participle": "lost", "Gerund": "losing"},
    "make": {"Present": "make / makes", "Past": "made", "Past Participle": "made", "Gerund": "making"},
    "meet": {"Present": "meet / meets", "Past": "met", "Past Participle": "met", "Gerund": "meeting"},
    "pay": {"Present": "pay / pays", "Past": "paid", "Past Participle": "paid", "Gerund": "paying"},
    "put": {"Present": "put / puts", "Past": "put", "Past Participle": "put", "Gerund": "putting"},
    "read": {"Present": "read / reads", "Past": "read", "Past Participle": "read", "Gerund": "reading"},
    "run": {"Present": "run / runs", "Past": "ran", "Past Participle": "run", "Gerund": "running"},
    "say": {"Present": "say / says", "Past": "said", "Past Participle": "said", "Gerund": "saying"}
}
# --- Interação com o usuário ---
if menu == "Escuta 🎧":
    st.subheader("Ouça frases em inglês")
    frase = st.text_input("Digite uma frase em inglês:")
    if st.button("Ouvir"):
        audio_html = gerar_audio(frase)
        st.markdown(audio_html, unsafe_allow_html=True)

elif menu == "Tradução 🌍":
    st.subheader("Tradução de textos com Google Translator")
    if "translation_google_text" not in st.session_state:
        st.session_state.translation_google_text = ""
    if "translation_google_direction" not in st.session_state:
        st.session_state.translation_google_direction = ""

    texto = st.text_area(
        "Digite o texto para traduzir",
        height=180,
        placeholder="Escreva ou cole aqui...",
    )
    direcao = st.radio(
        "Direção da tradução",
        ["Português → Inglês", "Inglês → Português"],
        horizontal=True,
    )

    if st.button("Traduzir texto", key="btn_traducao_google"):
        if not (texto or "").strip():
            st.warning("Digite um texto para traduzir.")
        else:
            origem, destino = ("pt", "en") if direcao == "Português → Inglês" else ("en", "pt")
            status = st.empty()
            barra_slot = st.empty()
            barra = barra_slot.progress(0)

            def _on_progress(atual, total):
                percentual = int((atual / total) * 100) if total else 100
                status.caption(f"Traduzindo parte {atual}/{total}...")
                barra.progress(percentual)

            try:
                traducao = traduzir_texto_google(
                    texto,
                    origem=origem,
                    destino=destino,
                    progress_callback=_on_progress,
                )
                st.session_state.translation_google_text = traducao
                st.session_state.translation_google_direction = direcao
                status.caption("Tradução concluída.")
            except Exception:
                st.session_state.translation_google_text = ""
                st.session_state.translation_google_direction = ""
                status.empty()
                st.error("Não foi possível traduzir no momento. Tente novamente em instantes.")
            finally:
                barra_slot.empty()

    if st.session_state.translation_google_text:
        st.success(st.session_state.translation_google_text)

        if st.session_state.translation_google_direction == "Português → Inglês":
            sotaque_opcao = st.selectbox(
                "Sotaque para ouvir a tradução em inglês",
                [
                    "Americano (EUA)",
                    "Britânico (Reino Unido)",
                    "Global (Neutro)",
                    "Indiano",
                    "Australiano",
                    "Irlandês",
                    "Sul-africano",
                    "Nigeriano",
                    "Asiático (Hong Kong)",
                ],
                index=0,
                key="translation_audio_accent",
            )
            st.caption("A disponibilidade de sotaques depende do serviço de voz do Google para cada região.")
            if st.button("Ouvir tradução em inglês", key="btn_ouvir_traducao_en"):
                audio_html = gerar_audio_ingles_sotaque(
                    st.session_state.translation_google_text,
                    sotaque=sotaque_opcao,
                )
                st.markdown(audio_html, unsafe_allow_html=True)

elif menu == "Dicionário 🇺🇸":
    st.subheader("Dicionário Inglês-Inglês (foco em uso americano)")
    st.caption("Consulte definição, classe gramatical, exemplo e pronúncia em inglês.")

    default_mw_key = os.getenv("MERRIAM_WEBSTER_API_KEY", "")
    merriam_api_key = st.text_input(
        "Merriam-Webster API Key (opcional)",
        value=default_mw_key,
        type="password",
        help="Se informada, o app prioriza Merriam-Webster; sem chave, usa fallback público.",
    )

    if "dictionary_result" not in st.session_state:
        st.session_state.dictionary_result = None

    termo = st.text_input("Digite uma palavra em inglês", placeholder="Ex.: schedule")

    if st.button("Buscar no dicionário", key="btn_dictionary_lookup"):
        termo_limpo = (termo or "").strip()
        if not termo_limpo:
            st.warning("Digite uma palavra para buscar.")
        else:
            try:
                st.session_state.dictionary_result = buscar_dicionario_ingles(
                    termo_limpo,
                    merriam_api_key=merriam_api_key,
                )
            except Exception:
                st.session_state.dictionary_result = {"found": False, "word": termo_limpo}
                st.error("Não foi possível consultar o dicionário no momento.")

    resultado = st.session_state.dictionary_result
    if resultado:
        if not resultado.get("found"):
            st.info(f"Nenhum resultado encontrado para: {resultado.get('word', '')}")
            if resultado.get("suggestions"):
                st.caption("Sugestões: " + ", ".join(resultado.get("suggestions", [])))
        else:
            st.markdown(f"### {resultado.get('word', '')}")
            if resultado.get("source"):
                st.caption(f"Fonte: {resultado.get('source')}")
            if resultado.get("phonetic"):
                st.caption(f"Pronúncia: {resultado['phonetic']}")
            if resultado.get("audio_url"):
                st.audio(resultado["audio_url"], format="audio/mp3")

            for meaning in resultado.get("meanings", []):
                st.write(f"**{meaning.get('part_of_speech', '-')}**")
                for i, definicao in enumerate(meaning.get("definitions", []), start=1):
                    st.write(f"{i}. {definicao.get('definition', '')}")
                    if definicao.get("example"):
                        st.caption(f"Exemplo: {definicao['example']}")
                sinonimos = meaning.get("synonyms", [])
                if sinonimos:
                    st.caption("Sinônimos: " + ", ".join(sinonimos))
                st.divider()

elif menu == "Conjugação 🔄":
    st.subheader("Conjugação de verbos irregulares")
    verbo = st.selectbox("Escolha um verbo:", list(conjugacoes.keys()))
    if verbo:
        tempos = conjugacoes[verbo]
        st.write(f"**Present:** {tempos['Present']}")
        st.write(f"**Past:** {tempos['Past']}")
        st.write(f"**Past Participle:** {tempos['Past Participle']}")
        st.write(f"**Gerund:** {tempos['Gerund']}")

elif menu == "Leitura 📖":
    st.subheader("Leitura com textos em domínio público")
    st.caption("Leia textos clássicos em inglês e ouça para treinar pronúncia.")
    modo_bilingue = st.toggle("Modo bilíngue lado a lado", value=False)

    fonte_leitura = st.radio(
        "Fonte do texto",
        ["Texto público", "Texto manual"],
        horizontal=True,
    )

    texto_conteudo = ""
    chave_base = ""

    if fonte_leitura == "Texto público":
        st.markdown("### Atualização de textos públicos")
        auto_texto_publico = st.toggle(
            "Adicionar automaticamente novos textos públicos (diário)",
            value=True,
            key="auto_public_text_daily",
        )
        qtd_texto_publico = st.selectbox(
            "Qtd. de novos textos por dia",
            [1, 2],
            index=0,
            key="daily_public_text_count",
        )
        incluir_online_publico = st.checkbox(
            "Complementar com textos online (Gutendex)",
            value=True,
            key="include_online_public_texts",
        )
        ultima_data_publico = get_last_public_text_update_date()
        st.caption(f"Última atualização diária: {ultima_data_publico or '-'}")

        hoje_utc_publico = datetime.now(timezone.utc).date().isoformat()
        if auto_texto_publico and ultima_data_publico != hoje_utc_publico:
            adicionados_hoje = incorporate_daily_public_texts(
                limit=qtd_texto_publico,
                include_online=incluir_online_publico,
            )
            set_last_public_text_update_date(hoje_utc_publico)
            st.caption(f"Atualização diária executada: {adicionados_hoje} novo(s) texto(s) incorporado(s).")

        if st.button("Buscar novos textos públicos agora"):
            adicionados_agora = incorporate_daily_public_texts(
                limit=qtd_texto_publico,
                include_online=incluir_online_publico,
            )
            st.success(f"{adicionados_agora} novo(s) texto(s) público(s) incorporado(s).")

        if st.button("Buscar somente textos online agora"):
            adicionados_online = fetch_and_incorporate_online_public_texts(limit=qtd_texto_publico)
            if adicionados_online > 0:
                st.success(f"{adicionados_online} novo(s) texto(s) online incorporado(s).")
            else:
                st.warning("A busca online foi executada, mas nenhum novo texto foi incorporado.")

        status_online = get_last_online_public_text_fetch_status()
        if status_online.get("updated_at"):
            st.caption(
                "Status da busca online: "
                f"{status_online.get('status', '-')} | "
                f"{status_online.get('updated_at', '-')}"
            )
            if status_online.get("details"):
                st.info(status_online.get("details", ""))

        titulos_publicos = list_public_titles()
        if not titulos_publicos:
            st.warning("Nenhum texto público disponível no momento.")
        else:
            titulo_escolhido = st.selectbox("Escolha um texto:", titulos_publicos)
            texto_info = get_public_text_by_title(titulo_escolhido)
            texto_conteudo = texto_info.get("text", "")
            chave_base = titulo_escolhido

            st.write(
                f"**Autor:** {texto_info.get('author', '-')} | "
                f"**Ano:** {texto_info.get('year', '-')} | "
                f"**Fonte:** {texto_info.get('source', '-')}"
            )

            st.text_area(
                "Texto em inglês",
                value=texto_conteudo,
                height=260,
                disabled=True,
            )
    else:
        st.markdown("### Texto manual")

        arquivo_txt = st.file_uploader(
            "Importar arquivo .txt",
            type=["txt"],
            key="reading_txt_uploader",
            help="Carrega o conteúdo do arquivo para edição no campo abaixo.",
        )
        if arquivo_txt is not None:
            raw_bytes = arquivo_txt.getvalue()
            try:
                conteudo_txt = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                conteudo_txt = raw_bytes.decode("latin-1")
            st.session_state.reading_manual_input = conteudo_txt.strip()
            nome_base = Path(arquivo_txt.name).stem.strip()
            if nome_base:
                st.session_state.reading_manual_title = nome_base
            st.success("Texto .txt carregado no campo manual.")

        textos_salvos = load_manual_reading_texts()
        titulos_salvos = [item["title"] for item in textos_salvos]
        opcoes_salvas = ["Nenhum"] + titulos_salvos
        st.session_state.reading_manual_selected = st.selectbox(
            "Favoritos salvos",
            opcoes_salvas,
            key="reading_saved_selector",
        )

        col_carregar_fav, col_excluir_fav = st.columns(2)
        with col_carregar_fav:
            if st.button("Carregar favorito"):
                if st.session_state.reading_manual_selected == "Nenhum":
                    st.warning("Selecione um favorito para carregar.")
                else:
                    favorito = next(
                        (item for item in textos_salvos if item["title"] == st.session_state.reading_manual_selected),
                        None,
                    )
                    if favorito:
                        st.session_state.reading_manual_input = favorito["text"]
                        st.session_state.reading_manual_title = favorito["title"]
                        st.success("Favorito carregado no editor.")
                        st.rerun()
        with col_excluir_fav:
            if st.button("Excluir favorito"):
                if st.session_state.reading_manual_selected == "Nenhum":
                    st.warning("Selecione um favorito para excluir.")
                else:
                    restantes = [
                        item for item in textos_salvos if item["title"] != st.session_state.reading_manual_selected
                    ]
                    save_manual_reading_texts(restantes)
                    st.session_state.reading_manual_selected = "Nenhum"
                    st.success("Favorito excluído.")
                    st.rerun()

        st.session_state.reading_manual_title = st.text_input(
            "Título do favorito",
            value=st.session_state.reading_manual_title,
            key="reading_manual_title_input",
        )

        texto_conteudo = st.text_area(
            "Cole ou escreva seu texto em inglês",
            value=st.session_state.reading_manual_input,
            height=260,
            placeholder="Paste your English text here...",
            key="reading_manual_textarea",
        ).strip()
        st.session_state.reading_manual_input = texto_conteudo

        col_salvar_fav, col_limpar_manual = st.columns(2)
        with col_salvar_fav:
            if st.button("Salvar/Atualizar favorito"):
                titulo = st.session_state.reading_manual_title.strip() or "Meu texto"
                if not texto_conteudo:
                    st.warning("Digite ou carregue um texto antes de salvar.")
                else:
                    now_iso = datetime.now(timezone.utc).isoformat()
                    atualizado = False
                    for item in textos_salvos:
                        if item["title"].casefold() == titulo.casefold():
                            item["title"] = titulo
                            item["text"] = texto_conteudo
                            item["updated_at"] = now_iso
                            atualizado = True
                            break
                    if not atualizado:
                        textos_salvos.append(
                            {
                                "title": titulo,
                                "text": texto_conteudo,
                                "updated_at": now_iso,
                            }
                        )
                    save_manual_reading_texts(textos_salvos)
                    st.success("Favorito salvo com sucesso.")
        with col_limpar_manual:
            if st.button("Limpar texto manual"):
                st.session_state.reading_manual_input = ""
                st.rerun()

        if texto_conteudo:
            digest = hashlib.sha1(texto_conteudo.encode("utf-8")).hexdigest()[:12]
            chave_base = f"manual::{digest}"
        else:
            st.info("Adicione um texto manual para habilitar tradução, áudio e prática por parágrafo.")

    if texto_conteudo:
        def traduzir_texto_leitura_com_progresso(texto_alvo):
            status = st.empty()
            barra_slot = st.empty()
            barra = barra_slot.progress(0)

            def _on_progress(atual, total):
                percentual = int((atual / total) * 100) if total else 100
                status.caption(f"Traduzindo parte {atual}/{total}...")
                barra.progress(percentual)

            try:
                traducao = traduzir_texto(
                    texto_alvo,
                    origem="en",
                    destino="pt",
                    progress_callback=_on_progress,
                )
                status.caption("Tradução concluída.")
                return traducao
            finally:
                barra_slot.empty()

        chave_texto = f"full::{chave_base}"
        if modo_bilingue and chave_texto not in st.session_state.reading_translation_cache:
            try:
                st.session_state.reading_translation_cache[chave_texto] = traduzir_texto_leitura_com_progresso(texto_conteudo)
            except Exception:
                st.session_state.reading_translation_cache[chave_texto] = "Tradução indisponível no momento."

        if modo_bilingue and chave_texto in st.session_state.reading_translation_cache:
            st.markdown("### Texto bilíngue")
            col_en_full, col_pt_full = st.columns(2)
            with col_en_full:
                st.markdown("**English**")
                st.info(texto_conteudo)
            with col_pt_full:
                st.markdown("**Português**")
                st.success(st.session_state.reading_translation_cache[chave_texto])

        col_traduzir_texto, col_mostrar_texto = st.columns(2)
        with col_traduzir_texto:
            if st.button("Traduzir texto completo"):
                if chave_texto not in st.session_state.reading_translation_cache:
                    try:
                        st.session_state.reading_translation_cache[chave_texto] = traduzir_texto_leitura_com_progresso(texto_conteudo)
                    except Exception:
                        st.session_state.reading_translation_cache[chave_texto] = "Tradução indisponível no momento."
        with col_mostrar_texto:
            if st.button("Limpar tradução do texto"):
                st.session_state.reading_translation_cache.pop(chave_texto, None)

        if chave_texto in st.session_state.reading_translation_cache and not modo_bilingue:
            st.markdown("### Tradução do texto")
            st.info(st.session_state.reading_translation_cache[chave_texto])

        velocidade_audio = st.slider(
            "Velocidade do áudio",
            min_value=0.75,
            max_value=1.50,
            value=1.00,
            step=0.05,
        )

        col_texto, col_paragrafo = st.columns(2)
        with col_texto:
            if st.button("Ouvir texto completo"):
                audio_html = gerar_audio(texto_conteudo, playback_rate=velocidade_audio)
                st.markdown(audio_html, unsafe_allow_html=True)

        paragrafos = split_public_paragraphs(texto_conteudo)
        with col_paragrafo:
            if paragrafos:
                indice_paragrafo = st.selectbox(
                    "Parágrafo para ouvir",
                    list(range(1, len(paragrafos) + 1)),
                )
                paragrafo_escolhido = paragrafos[indice_paragrafo - 1]
                chave_paragrafo = f"paragraph::{chave_base}::{indice_paragrafo}"

                if modo_bilingue and chave_paragrafo not in st.session_state.reading_translation_cache:
                    try:
                        st.session_state.reading_translation_cache[chave_paragrafo] = traduzir_texto_leitura_com_progresso(paragrafo_escolhido)
                    except Exception:
                        st.session_state.reading_translation_cache[chave_paragrafo] = "Tradução indisponível no momento."

                if st.button("Ouvir parágrafo"):
                    audio_html = gerar_audio(
                        paragrafo_escolhido,
                        playback_rate=velocidade_audio,
                    )
                    st.markdown(audio_html, unsafe_allow_html=True)

                col_traduzir_paragrafo, col_limpar_paragrafo = st.columns(2)
                with col_traduzir_paragrafo:
                    if st.button("Traduzir parágrafo"):
                        if chave_paragrafo not in st.session_state.reading_translation_cache:
                            try:
                                st.session_state.reading_translation_cache[chave_paragrafo] = traduzir_texto_leitura_com_progresso(paragrafo_escolhido)
                            except Exception:
                                st.session_state.reading_translation_cache[chave_paragrafo] = "Tradução indisponível no momento."
                with col_limpar_paragrafo:
                    if st.button("Limpar tradução do parágrafo"):
                        st.session_state.reading_translation_cache.pop(chave_paragrafo, None)

                st.markdown("### Parágrafo selecionado")
                if modo_bilingue and chave_paragrafo in st.session_state.reading_translation_cache:
                    col_en, col_pt = st.columns(2)
                    with col_en:
                        st.markdown("**English**")
                        st.info(paragrafo_escolhido)
                    with col_pt:
                        st.markdown("**Português**")
                        st.success(st.session_state.reading_translation_cache[chave_paragrafo])
                else:
                    st.info(paragrafo_escolhido)

                if chave_paragrafo in st.session_state.reading_translation_cache and not modo_bilingue:
                    st.markdown("### Tradução do parágrafo")
                    st.success(st.session_state.reading_translation_cache[chave_paragrafo])

elif menu == "Frases do dia a dia 💬":
    st.subheader("Frases do inglês americano por contexto")
    st.caption("Veja quando usar cada frase e a melhor tradução para o português. Também é possível adicionar frases novas.")

    with st.expander("Importar ou exportar frases em lote"):
        st.write("Use JSON ou CSV para adicionar várias frases de uma vez.")
        st.caption("CSV esperado: context,english,when_to_use,best_translation")

        modelo_frases = [
            {
                "context": "Trabalho",
                "english": "I'll get back to you by noon.",
                "when_to_use": "Para confirmar retorno com prazo no trabalho.",
                "best_translation": "Te dou retorno até o meio-dia.",
            },
            {
                "context": "Restaurante",
                "english": "Could we have some water, please?",
                "when_to_use": "Para pedir água ao garçom.",
                "best_translation": "Podemos pedir água, por favor?",
            },
        ]
        modelo_json = json.dumps(modelo_frases, ensure_ascii=False, indent=2)
        modelo_csv = (
            "context,english,when_to_use,best_translation\n"
            'Trabalho,"I\'ll get back to you by noon.","Para confirmar retorno com prazo no trabalho.","Te dou retorno até o meio-dia."\n'
            'Restaurante,"Could we have some water, please?","Para pedir água ao garçom.","Podemos pedir água, por favor?"\n'
        )

        col_modelo_json, col_modelo_csv = st.columns(2)
        with col_modelo_json:
            st.download_button(
                label="Baixar modelo de importação (JSON)",
                data=modelo_json,
                file_name="daily_phrases_modelo.json",
                mime="application/json",
            )
        with col_modelo_csv:
            st.download_button(
                label="Baixar modelo de importação (CSV)",
                data=modelo_csv,
                file_name="daily_phrases_modelo.csv",
                mime="text/csv",
            )

        arquivo = st.file_uploader("Selecione um arquivo .json ou .csv", type=["json", "csv"])
        if arquivo is not None:
            try:
                conteudo = decode_uploaded_text(arquivo.getvalue())
            except Exception:
                st.error("Não foi possível ler o arquivo enviado. Verifique a codificação e tente novamente.")
                conteudo = ""
            nome = (arquivo.name or "").lower()
            try:
                if nome.endswith(".json"):
                    frases_importadas = parse_phrases_json(conteudo)
                elif nome.endswith(".csv"):
                    frases_importadas = parse_phrases_csv(conteudo)
                else:
                    frases_importadas = []

                resumo = save_extra_phrases_bulk(frases_importadas)
                st.success(
                    f"Importação concluída. Adicionadas: {resumo['added']} | "
                    f"Duplicadas: {resumo['duplicates']} | Inválidas: {resumo['invalid']}"
                )
            except Exception:
                st.error("Não foi possível importar o arquivo. Verifique o formato e tente novamente.")

        col_export_json, col_export_csv = st.columns(2)
        with col_export_json:
            st.download_button(
                label="Exportar frases (JSON)",
                data=export_all_phrases_json(),
                file_name="daily_phrases_export.json",
                mime="application/json",
            )
        with col_export_csv:
            st.download_button(
                label="Exportar frases (CSV)",
                data=export_all_phrases_csv(),
                file_name="daily_phrases_export.csv",
                mime="text/csv",
            )

    contextos = ["Todos"] + list_contexts()
    contexto_escolhido = st.selectbox("Escolha um contexto:", contextos)
    busca = st.text_input("Buscar frase, tradução ou contexto:")
    apenas_favoritas = st.checkbox("Mostrar apenas favoritas")

    col_sugerir, col_quantidade = st.columns([2, 1])
    with col_quantidade:
        quantidade_sugestao = st.selectbox("Qtd. sugestões", [1, 2, 3, 4, 5], index=2)
    with col_sugerir:
        st.write("")
        if st.button("Gerar novas frases automaticamente"):
            sugestoes = suggest_new_phrases(contexto_escolhido, limit=quantidade_sugestao)
            if not sugestoes:
                st.info("Não há novas sugestões disponíveis para este contexto agora.")
            else:
                adicionadas = 0
                for sugestao in sugestoes:
                    if save_extra_phrase(sugestao):
                        adicionadas += 1
                st.success(f"{adicionadas} nova(s) frase(s) adicionada(s) ao módulo.")

    st.write("### Expandir com frases da internet")
    auto_diario = st.toggle("Atualização diária automática ao abrir este módulo", value=True)
    limite_auto_diario = st.selectbox("Qtd. diária automática", [1, 2, 3], index=1)
    ultima_data_auto = get_last_auto_update_date()
    st.caption(f"Ultima auto-incorporacao registrada: {ultima_data_auto or '-'}")

    if auto_diario:
        hoje_utc = datetime.now(timezone.utc).date().isoformat()
        if ultima_data_auto != hoje_utc:
            frases_auto = fetch_online_phrases(limit=limite_auto_diario, force_refresh=False)
            adicionadas_auto = incorporar_frases_online(frases_auto)
            set_last_auto_update_date(hoje_utc)
            st.caption(f"Atualização diária executada: {adicionadas_auto} nova(s) frase(s) incorporada(s).")

    col_online, col_online_qtd = st.columns([2, 1])
    cache_info = get_online_cache_info()
    st.caption(
        f"Cache online: {cache_info['status']} | Atualizado em: {cache_info['updated_at']} | Frases em cache: {cache_info['count']}"
    )

    forcar_atualizacao = st.checkbox("Forçar atualização online (ignorar cache)")
    with col_online_qtd:
        quantidade_online = st.selectbox("Qtd. online", [1, 2, 3, 4, 5], index=1)
    with col_online:
        st.write("")
        if st.button("Buscar e incorporar frases online"):
            frases_online = fetch_online_phrases(
                limit=quantidade_online,
                force_refresh=forcar_atualizacao,
            )
            if not frases_online:
                st.info("Nao foi possivel obter frases novas da internet agora.")
            else:
                adicionadas_online = incorporar_frases_online(frases_online)
                st.success(f"{adicionadas_online} frase(s) online incorporada(s) com sucesso.")

    with st.expander("Adicionar frase manualmente"):
        with st.form("form_nova_frase"):
            contexto_novo = st.text_input("Contexto")
            english_novo = st.text_input("Frase em inglês")
            when_to_use_novo = st.text_area("Quando usar")
            traducao_nova = st.text_input("Melhor tradução")
            submit_nova = st.form_submit_button("Salvar frase")

            if submit_nova:
                if not contexto_novo or not english_novo or not when_to_use_novo or not traducao_nova:
                    st.warning("Preencha todos os campos para salvar.")
                else:
                    nova_frase = {
                        "context": contexto_novo.strip(),
                        "english": english_novo.strip(),
                        "when_to_use": when_to_use_novo.strip(),
                        "best_translation": traducao_nova.strip(),
                    }
                    if save_extra_phrase(nova_frase):
                        st.success("Frase adicionada com sucesso.")
                    else:
                        st.info("Essa frase já existe no módulo.")

    frases = filter_phrases(contexto_escolhido)

    if busca:
        termo = busca.strip().lower()
        frases = [
            frase for frase in frases
            if termo in frase["english"].lower()
            or termo in frase["best_translation"].lower()
            or termo in frase["when_to_use"].lower()
            or termo in frase["context"].lower()
        ]

    if apenas_favoritas:
        frases = [
            frase for frase in frases
            if f"{frase['context']}::{frase['english']}" in st.session_state.favorite_phrases
        ]

    st.markdown("### Quiz randômico (frente e verso)")
    if not frases:
        st.info("Ajuste os filtros para gerar perguntas no quiz.")
    else:
        if "daily_quiz_card" not in st.session_state:
            st.session_state.daily_quiz_card = None
        if "daily_quiz_show_answer" not in st.session_state:
            st.session_state.daily_quiz_show_answer = False
        if "daily_quiz_hits" not in st.session_state:
            st.session_state.daily_quiz_hits = 0
        if "daily_quiz_misses" not in st.session_state:
            st.session_state.daily_quiz_misses = 0
        if "daily_quiz_round" not in st.session_state:
            st.session_state.daily_quiz_round = 0

        modo_quiz = st.radio(
            "Direção do quiz",
            ["Frente (EN → PT)", "Verso (PT → EN)", "Misto aleatório"],
            horizontal=True,
            key="daily_quiz_mode",
        )

        def _gerar_quiz_card(pool):
            frase = random.choice(pool)
            if modo_quiz == "Misto aleatório":
                direcao = random.choice(["frente", "verso"])
            elif modo_quiz == "Verso (PT → EN)":
                direcao = "verso"
            else:
                direcao = "frente"

            if direcao == "frente":
                pergunta = frase["english"]
                resposta = frase["best_translation"]
                label = "EN → PT"
            else:
                pergunta = frase["best_translation"]
                resposta = frase["english"]
                label = "PT → EN"

            return {
                "id": f"{frase['context']}::{frase['english']}",
                "context": frase["context"],
                "when_to_use": frase["when_to_use"],
                "pergunta": pergunta,
                "resposta": resposta,
                "label": label,
            }

        ids_disponiveis = {f"{f['context']}::{f['english']}" for f in frases}
        card_atual = st.session_state.daily_quiz_card
        if card_atual is None or card_atual.get("id") not in ids_disponiveis:
            st.session_state.daily_quiz_card = _gerar_quiz_card(frases)
            st.session_state.daily_quiz_show_answer = False
            st.session_state.daily_quiz_round += 1

        col_quiz_nova, col_quiz_hits, col_quiz_misses = st.columns([2, 1, 1])
        with col_quiz_nova:
            if st.button("Nova pergunta aleatória"):
                st.session_state.daily_quiz_card = _gerar_quiz_card(frases)
                st.session_state.daily_quiz_show_answer = False
                st.session_state.daily_quiz_round += 1
                st.rerun()
        with col_quiz_hits:
            st.metric("Acertos", st.session_state.daily_quiz_hits)
        with col_quiz_misses:
            st.metric("Erros", st.session_state.daily_quiz_misses)

        card = st.session_state.daily_quiz_card
        st.caption(f"Pergunta ({card['label']}) | Contexto: {card['context']}")
        st.info(card["pergunta"])
        input_key = f"daily_quiz_user_answer_{st.session_state.daily_quiz_round}"
        st.text_input("Sua resposta (opcional)", key=input_key)

        col_quiz_resposta, col_quiz_acerto, col_quiz_erro, col_quiz_proxima = st.columns(4)
        with col_quiz_resposta:
            if st.button("Mostrar resposta"):
                st.session_state.daily_quiz_show_answer = True
        with col_quiz_acerto:
            if st.button("Marcar acerto"):
                st.session_state.daily_quiz_hits += 1
                st.session_state.daily_quiz_card = _gerar_quiz_card(frases)
                st.session_state.daily_quiz_show_answer = False
                st.session_state.daily_quiz_round += 1
                st.rerun()
        with col_quiz_erro:
            if st.button("Marcar erro"):
                st.session_state.daily_quiz_misses += 1
                st.session_state.daily_quiz_card = _gerar_quiz_card(frases)
                st.session_state.daily_quiz_show_answer = False
                st.session_state.daily_quiz_round += 1
                st.rerun()
        with col_quiz_proxima:
            if st.button("Próxima"):
                st.session_state.daily_quiz_card = _gerar_quiz_card(frases)
                st.session_state.daily_quiz_show_answer = False
                st.session_state.daily_quiz_round += 1
                st.rerun()

        if st.session_state.daily_quiz_show_answer:
            st.success(f"Resposta: {card['resposta']}")
            st.caption(f"Quando usar: {card['when_to_use']}")

    if not frases:
        st.info("Nenhuma frase encontrada para este contexto.")
    else:
        for indice, frase in enumerate(frases):
            phrase_id = f"{frase['context']}::{frase['english']}"
            favorita = phrase_id in st.session_state.favorite_phrases

            st.markdown(f"### {frase['english']}")
            st.write(f"**Contexto:** {frase['context']}")
            st.write(f"**Quando usar:** {frase['when_to_use']}")
            st.write(f"**Melhor tradução:** {frase['best_translation']}")

            col_ouvir, col_favorita = st.columns([2, 1])
            with col_ouvir:
                if st.button(f"Ouvir: {frase['english']}", key=f"ouvir_{indice}_{phrase_id}"):
                    audio_html = gerar_audio(frase['english'])
                    st.markdown(audio_html, unsafe_allow_html=True)
            with col_favorita:
                texto_favorita = "Desfavoritar" if favorita else "Favoritar"
                if st.button(texto_favorita, key=f"favorita_{indice}_{phrase_id}"):
                    if favorita:
                        st.session_state.favorite_phrases.remove(phrase_id)
                    else:
                        st.session_state.favorite_phrases.add(phrase_id)
                    save_favorite_phrases(st.session_state.favorite_phrases)

            if favorita:
                st.caption("Salva para revisão")

            st.divider()

    if st.session_state.favorite_phrases:
        st.markdown("### Frases favoritas")
        for phrase_id in sorted(st.session_state.favorite_phrases):
            contexto, frase_ingles = phrase_id.split("::", 1)

            st.write(f"- [{contexto}] {frase_ingles}")

elif menu == "Podcast de Notícias 🎙️":
    st.subheader("Podcast de notícias atuais do mundo (em inglês)")
    st.caption(
        "Manchetes atuais em inglês narradas em áudio, com legenda opcional em português, "
        "inglês ou nos dois idiomas lado a lado."
    )

    qtd_noticias = st.slider("Quantidade de manchetes no episódio", min_value=3, max_value=8, value=5)
    forcar_atualizacao_noticias = st.checkbox("Forçar busca de notícias novas agora", value=False)

    if st.button("Gerar episódio de hoje"):
        with st.spinner("Buscando manchetes atuais..."):
            noticias_buscadas = npc.get_world_news(limit=qtd_noticias, force_refresh=forcar_atualizacao_noticias)
        st.session_state.podcast_news_items = noticias_buscadas
        st.session_state.podcast_translation_cache = {}
        if not noticias_buscadas:
            st.error("Não foi possível buscar notícias no momento. Tente novamente em instantes.")

    info_cache_noticias = npc.get_cache_info()
    if info_cache_noticias.get("updated_at"):
        st.caption(f"Última busca de notícias: {info_cache_noticias.get('updated_at', '-')}")

    noticias_episodio = st.session_state.podcast_news_items
    if not noticias_episodio:
        st.info("Clique em 'Gerar episódio de hoje' para buscar as manchetes atuais.")
    else:
        legenda_opcao = st.radio(
            "Legenda",
            ["Inglês", "Português", "Bilíngue (Inglês + Português)"],
            horizontal=True,
            key="podcast_legenda_opcao",
        )

        velocidade_podcast = st.slider(
            "Velocidade da narração",
            min_value=0.75,
            max_value=1.50,
            value=1.00,
            step=0.05,
            key="podcast_speed",
        )

        roteiro_completo = npc.build_episode_script(noticias_episodio)

        col_ouvir_ep, col_baixar_ep = st.columns(2)
        with col_ouvir_ep:
            if st.button("Ouvir episódio completo"):
                audio_html = gerar_audio(roteiro_completo, playback_rate=velocidade_podcast)
                st.markdown(audio_html, unsafe_allow_html=True)
        with col_baixar_ep:
            st.download_button(
                label="Baixar roteiro (texto)",
                data=roteiro_completo,
                file_name="podcast_noticias.txt",
                mime="text/plain",
            )

        def _traduzir_noticia_podcast(texto_alvo):
            try:
                return traduzir_texto_google(texto_alvo, origem="en", destino="pt")
            except Exception:
                return "Tradução indisponível no momento."

        st.markdown("### Manchetes do episódio")
        for indice_noticia, item_noticia in enumerate(noticias_episodio, start=1):
            titulo_noticia = item_noticia.get("title", "")
            resumo_noticia = item_noticia.get("summary", "")
            fonte_noticia = item_noticia.get("source", "")
            link_noticia = item_noticia.get("link", "")
            texto_en_noticia = f"{titulo_noticia}. {resumo_noticia}".strip()
            chave_traducao_noticia = f"{indice_noticia}::{titulo_noticia}"

            st.markdown(f"**{indice_noticia}. {titulo_noticia}**")
            rodape_fonte = f"Fonte: {fonte_noticia}" + (f" — {link_noticia}" if link_noticia else "")
            st.caption(rodape_fonte)

            if legenda_opcao == "Inglês":
                st.info(texto_en_noticia)
            elif legenda_opcao == "Português":
                if chave_traducao_noticia not in st.session_state.podcast_translation_cache:
                    st.session_state.podcast_translation_cache[chave_traducao_noticia] = _traduzir_noticia_podcast(
                        texto_en_noticia
                    )
                st.success(st.session_state.podcast_translation_cache[chave_traducao_noticia])
            else:
                if chave_traducao_noticia not in st.session_state.podcast_translation_cache:
                    st.session_state.podcast_translation_cache[chave_traducao_noticia] = _traduzir_noticia_podcast(
                        texto_en_noticia
                    )
                col_en_noticia, col_pt_noticia = st.columns(2)
                with col_en_noticia:
                    st.markdown("**English**")
                    st.info(texto_en_noticia)
                with col_pt_noticia:
                    st.markdown("**Português**")
                    st.success(st.session_state.podcast_translation_cache[chave_traducao_noticia])

            if st.button("Ouvir esta manchete", key=f"ouvir_noticia_{indice_noticia}"):
                audio_html = gerar_audio(texto_en_noticia, playback_rate=velocidade_podcast)
                st.markdown(audio_html, unsafe_allow_html=True)

            st.divider()

elif menu == "Chunks de Estudo 📚":
    st.subheader("Chunks de Estudo - Sistema de Aprendizado")
    st.caption("Gerencie frases de estudo, faça upload, download e use ferramentas de aprendizado")
    
    # Inicializa estatísticas
    if "chunks_stats" not in st.session_state:
        st.session_state.chunks_stats = ck.get_study_statistics()
    
    # Botão para atualizar estatísticas manualmente
    col_refresh, _ = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 Atualizar estatísticas"):
            st.session_state.chunks_stats = ck.get_study_statistics()
            st.rerun()
    
    stats = st.session_state.chunks_stats
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Chunks", stats.get('total_chunks', 0))
    with col2:
        st.metric("Chunks Estudados", stats.get('studied_chunks', 0))
    with col3:
        st.metric("Taxa de Sucesso", f"{stats.get('success_rate', 0):.1f}%")
    with col4:
        st.metric("Para Revisar Hoje", stats.get('chunks_to_review_today', 0))
    
    st.divider()
    
    # Abas de funcionalidades
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Listar Chunks", 
        "📤 Upload", 
        "📥 Download", 
        "🌐 Online", 
        "📚 Estudar"
    ])
    
    with tab1:
        st.markdown("### Listar e Filtrar Chunks")
        
        # Filtros
        col_ctx, col_diff = st.columns(2)
        with col_ctx:
            contexts = ["Todos"] + ck.list_contexts()
            context_filter = st.selectbox("Filtrar por Contexto", contexts)
        
        with col_diff:
            difficulties = ["Todos", "beginner", "intermediate", "advanced"]
            diff_filter = st.selectbox("Filtrar por Dificuldade", difficulties)
        
        # Busca
        search_query = st.text_input("Buscar (conteúdo, tradução ou contexto)")
        
        # Aplica filtros
        filtered_chunks = ck.filter_chunks(
            context=context_filter,
            difficulty=diff_filter
        )
        
        if search_query:
            filtered_chunks = ck.search_chunks(search_query)
        
        # Exibe chunks
        st.write(f"**Total encontrado:** {len(filtered_chunks)} chunks")
        
        for chunk in filtered_chunks[:20]:  # Limita a 20 para performance
            with st.expander(f"{chunk['content']} ({chunk['context']})"):
                st.write(f"**Tradução:** {chunk['translation']}")
                if chunk.get('when_to_use'):
                    st.write(f"**Quando usar:** {chunk['when_to_use']}")
                if chunk.get('difficulty'):
                    st.write(f"**Dificuldade:** {chunk['difficulty']}")
                if chunk.get('tags'):
                    st.write(f"**Tags:** {', '.join(chunk['tags'])}")
    
    with tab2:
        st.markdown("### Upload de Chunks")
        st.caption("Faça upload de arquivos JSON ou CSV com chunks")
        
        # Download modelo
        modelo_json = json.dumps([
            {
                "context": "Conversação Básica",
                "content": "How are you doing today?",
                "translation": "Como você está hoje?",
                "when_to_use": "Cumprimento informal",
                "difficulty": "beginner",
                "tags": ["greeting", "daily"]
            }
        ], ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📥 Baixar Modelo JSON",
            data=modelo_json,
            file_name="modelo_chunks.json",
            mime="application/json"
        )
        
        # Upload
        uploaded_file = st.file_uploader("Escolha um arquivo JSON ou CSV", type=["json", "csv"])
        
        if uploaded_file is not None:
            try:
                content = decode_uploaded_text(uploaded_file.getvalue())
                file_format = "json" if uploaded_file.name.endswith(".json") else "csv"
                
                # Valida
                validation = ck.validate_chunks_file(content, file_format)
                st.info(f"Arquivo válido: {validation['valid']} | Total: {validation['total']} | Válidos: {validation['valid_chunks']}")
                
                if st.button("Importar Chunks"):
                    result = ck.upload_chunks_from_file(content, file_format=file_format)
                    st.success(f"✅ Adicionados: {result['added']} | Duplicados: {result['duplicates']} | Inválidos: {result['invalid']}")
                    
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {str(e)}")
    
    with tab3:
        st.markdown("### Download e Exportação")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📥 Exportar Todos (JSON)"):
                json_data = ck.export_chunks_json()
                st.download_button(
                    label="💾 Baixar JSON",
                    data=json_data,
                    file_name="chuncks_export.json",
                    mime="application/json"
                )
        
        with col_export2:
            if st.button("📥 Exportar Todos (CSV)"):
                csv_data = ck.export_chunks_csv()
                st.download_button(
                    label="💾 Baixar CSV",
                    data=csv_data,
                    file_name="chuncks_export.csv",
                    mime="text/csv"
                )
        
        # Exportar por contexto
        st.markdown("### Exportar por Contexto")
        context_to_export = st.selectbox("Selecione o Contexto", ck.list_contexts())
        if st.button(f"Exportar {context_to_export}"):
            context_data = ck.export_chunks_by_context(context_to_export)
            st.download_button(
                label=f"💾 Baixar {context_to_export}",
                data=context_data,
                file_name=f"chuncks_{context_to_export.replace(' ', '_')}.json",
                mime="application/json"
            )
    
    with tab4:
        st.markdown("### Receber Chunks Online")
        st.caption("Busque frases autênticas em inglês com contexto")
        
        # Info do cache
        cache_info = ck.get_online_cache_info()
        st.caption(f"Cache: {cache_info['status']} | Atualizado: {cache_info['updated_at']} | Chunks em cache: {cache_info['count']}")
        
        col_online1, col_online2 = st.columns(2)
        
        with col_online1:
            limit_online = st.number_input("Quantidade", min_value=1, max_value=10, value=3)
            force_refresh = st.checkbox("Forçar atualização (ignorar cache)")
        
        with col_online2:
            st.write("")
            st.write("")
            if st.button("🌐 Buscar Chunks Online"):
                with st.spinner("Buscando frases online..."):
                    online_chunks = ck.fetch_online_chunks(limit=limit_online, force_refresh=force_refresh)
                    if online_chunks:
                        st.success(f"Encontrados {len(online_chunks)} chunks!")
                        for chunk in online_chunks:
                            st.write(f"- {chunk['content']} ({chunk['context']})")
                    else:
                        st.info("Nenhum chunk online disponível no momento.")
        
        if st.button("➕ Incorporar Chunks Online"):
            added = ck.incorporate_online_chunks(limit=limit_online)
            st.success(f"Chunks adicionados: {added}")
    
    with tab5:
        st.markdown("### Ferramentas de Estudo")
        
        # Estatísticas de estudo
        st.markdown("#### 📊 Estatísticas")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Total de Revisões", stats.get('total_reviews', 0))
        with col_stat2:
            st.metric("Tempo Total", f"{stats.get('total_time_minutes', 0):.1f} min")
        with col_stat3:
            st.metric("Sequência", f"{stats.get('streak_days', 0)} dias")
        
        st.divider()
        
        # Flashcards
        st.markdown("#### 🎴 Flashcards")
        col_flash1, col_flash2 = st.columns(2)
        with col_flash1:
            flashcard_limit = st.number_input("Quantidade", min_value=1, max_value=20, value=5, key="flashcard_limit")
            flashcard_context = st.selectbox("Contexto", ["Todos"] + ck.list_contexts(), key="flashcard_context")
        
        with col_flash2:
            st.write("")
            st.write("")
            if st.button("🎴 Gerar Flashcards"):
                flashcards = ck.generate_study_flashcards(limit=flashcard_limit, context=flashcard_context)
                for i, card in enumerate(flashcards, 1):
                    with st.expander(f"Flashcard {i}: {card['front'][:50]}..."):
                        st.write(f"**Frente:** {card['front']}")
                        st.write(f"**Verso:** {card['back']}")
                        st.caption(f"Contexto: {card['context']}")
        
        # Quiz
        st.markdown("#### ❓ Quiz de Tradução")
        col_quiz1, col_quiz2 = st.columns(2)
        with col_quiz1:
            quiz_limit = st.number_input("Quantidade", min_value=1, max_value=10, value=3, key="quiz_limit")
        
        with col_quiz2:
            st.write("")
            st.write("")
            if st.button("❓ Gerar Quiz"):
                quiz = ck.generate_quiz_questions(limit=quiz_limit)
                for i, question in enumerate(quiz, 1):
                    st.write(f"**Pergunta {i}:** {question['question']}")
                    for j, option in enumerate(question['options'], 1):
                        st.write(f"  [{j}] {option}")
                    with st.expander("Ver Resposta"):
                        st.success(f"Resposta: {question['correct_answer']}")
                        st.caption(f"Explicação: {question['explanation']}")
        
        # Fila de estudo
        st.markdown("#### 📚 Fila de Estudo (Spaced Repetition)")
        study_queue = ck.get_study_queue(limit=10)
        if study_queue:
            for i, chunk in enumerate(study_queue, 1):
                st.write(f"{i}. **{chunk['content']}** ({chunk.get('difficulty', 'N/A')})")
        else:
            st.info("Nenhum chunk na fila de estudo.")
