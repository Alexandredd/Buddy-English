# Buddy-English 🎯

**Sistema interativo de aprendizado de inglês americano** construído com Python e Streamlit.

## 📋 Visão Geral

O Buddy-English é uma plataforma completa para treinar inglês com foco em **inglês americano**. O sistema oferece múltiplas ferramentas integradas para praticar escuta, tradução, leitura, vocabulário e gramática, tudo em uma interface web interativa.

---

## ✨ Funcionalidades

### 🎧 Escuta
- Reprodução de áudio de frases em inglês com **gTTS**
- Controle de velocidade de reprodução (0.75x a 1.50x)
- Suporte a múltiplos sotaques: Americano, Britânico, Indiano, Australiano, Irlandês, Sul-africano, Nigeriano, Asiático

### 🌍 Tradução
- Tradução bidirecional **Português ↔ Inglês**
- Motor Google Translator (biblioteca ou fallback HTTP)
- Divisão automática de textos longos em partes
- Barra de progresso durante a tradução
- Áudio da tradução com seleção de sotaque

### 🇺🇸 Dicionário Inglês-Inglês
- Consulta a **Merriam-Webster** (com chave API opcional)
- Fallback para **Free Dictionary API** (público)
- Exibição de: definição, classe gramatical, pronúncia fonética, áudio, sinônimos
- Sugestões de palavras quando não encontra resultado

### 🔄 Conjugação de Verbos Irregulares
- 50 verbos irregulares do inglês
- Exibição dos tempos: Present, Past, Past Participle, Gerund

### 📖 Leitura
- Textos clássicos em **domínio público**
- **Modo bilíngue** lado a lado (inglês + português)
- Tradução de texto completo ou por parágrafo
- Áudio do texto completo ou parágrafo selecionado
- Importação de arquivos `.txt`
- Salvamento de textos favoritos
- Atualização automática diária de novos textos
- Integração com **Gutendex** (Projeto Gutenberg) para textos online

### 💬 Frases do Dia a Dia
- Frases organizadas por **contexto** (Trabalho, Restaurante, Viagem, etc.)
- Filtro por contexto e busca textual
- **Quiz interativo** (frente/verso/misto)
- Sistema de **favoritos** para revisão
- Importação/exportação em **JSON** e **CSV**
- Geração automática de novas frases
- Busca e incorporação de frases online
- Atualização diária automática

### 🎙️ Podcast de Notícias
- Manchetes atuais do mundo em inglês
- Narração em áudio com controle de velocidade
- Legendas em: **Inglês**, **Português** ou **Bilíngue**
- Download do roteiro em texto
- Cache inteligente de notícias

### 📚 Chunks de Estudo
- **8 chunks base** pré-carregados por contexto
- Adicionar chunks manualmente ou em lote
- Upload via **JSON** ou **CSV** com validação
- Exportação completa ou por contexto
- Busca de chunks online (Tatoeba, Quotable)
- **Sistema de Repetição Espaçada** (algoritmo SM-2 simplificado)
- **Flashcards** para estudo
- **Quiz de tradução** com múltipla escolha
- Estatísticas completas de estudo
- Insights personalizados de aprendizado
- Cache online com 24h de validade

### 📝 Corretor Ortográfico
- Correção de texto com **LanguageTool API**
- Fallback local com mais de **50 regras** de correção
- Correção de: ortografia, concordância, pontuação, expressões comuns
- Destaque de alterações com diff inline
- Refinamento opcional com **OpenAI** (GPT-4o-mini)
- Níveis de correção: Básico, Estrito, Nativo US

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- Pip (gerenciador de pacotes)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/Alexandredd/Buddy-English.git
cd Buddy-English

# Instale as dependências
pip install -r requirements.txt
```

### Executar

```bash
streamlit run app.py
```

Acesse no navegador: **http://localhost:8501**

---

## 📦 Estrutura do Projeto

```
Buddy-English/
├── app.py                          # Aplicação principal (Streamlit)
├── app_editor.py                   # Editor auxiliar
├── buddy_english_cli.py            # Interface de linha de comando
├── chuncks.py                      # Módulo de chunks de estudo
├── chuncks_example.py              # Exemplos de uso do módulo chunks
├── CHUNCKS_README.md               # Documentação do módulo chunks
├── compare_versions.py             # Comparador de versões
├── daily_phrases.py                # Módulo de frases do dia a dia
├── download_github.py              # Utilitário de download
├── news_podcast.py                 # Módulo de podcast de notícias
├── public_domain_texts.py          # Módulo de textos em domínio público
├── requirements.txt                # Dependências do projeto
├── .gitignore                      # Arquivos ignorados pelo Git
│
# Arquivos de dados (gerados automaticamente)
├── chuncks_data.json               # Chunks customizados
├── chuncks_study_progress.json     # Progresso de estudo
├── daily_phrases_extra.json        # Frases extras
├── daily_phrases_meta.json         # Metadados das frases
├── daily_phrases_online_cache.json # Cache de frases online
├── news_podcast_cache.json         # Cache de notícias
└── reading_manual_texts.json       # Textos manuais salvos
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| **Python** | 3.13+ | Linguagem principal |
| **Streamlit** | 1.59+ | Interface web interativa |
| **gTTS** | - | Síntese de voz (Google Text-to-Speech) |
| **pydub** | - | Processamento de áudio |
| **deep-translator** | - | Tradução Google Translator |
| **requests** | - | Requisições HTTP |
| **LanguageTool** | - | Corretor ortográfico |
| **OpenAI API** | - | Refinamento de texto (opcional) |
| **Merriam-Webster API** | - | Dicionário (opcional) |

---

## 🔧 Configuração

### Variáveis de Ambiente (Opcional)

| Variável | Descrição | Onde obter |
|----------|-----------|------------|
| `MERRIAM_WEBSTER_API_KEY` | Chave da API Merriam-Webster | [dictionaryapi.com](https://dictionaryapi.com/) |
| `OPENAI_API_KEY` | Chave da API OpenAI | [platform.openai.com](https://platform.openai.com/) |

### Dependências

```txt
streamlit>=1.28.0
requests>=2.31.0
gtts>=2.5.0
pydub>=0.25.1
deep-translator>=1.11.0
```

---

## 📊 Estatísticas do Sistema

- **8 módulos** de aprendizado integrados
- **50 verbos irregulares** com conjugação completa
- **8 chunks base** pré-carregados
- **Múltiplos contextos** de frases do dia a dia
- **Textos clássicos** em domínio público
- **Notícias atuais** do mundo em inglês
- **50+ regras** de correção ortográfica local
- **3 níveis** de refinamento com IA

---

## 🎯 Público-Alvo

- Estudantes de inglês de nível **básico a avançado**
- Brasileiros aprendendo **inglês americano**
- Profissionais que precisam de **inglês para negócios**
- Viajantes que querem **praticar situações reais**
- Autodidatas que buscam **ferramentas interativas**

---

## 📄 Licença

Projeto de código aberto para fins educacionais.

## 👨‍💻 Autor

**Alexandredd** - [GitHub](https://github.com/Alexandredd)

---

## 🙏 Agradecimentos

- [Streamlit](https://streamlit.io/) - Framework web
- [Google TTS](https://gtts.readthedocs.io/) - Síntese de voz
- [LanguageTool](https://languagetool.org/) - Corretor ortográfico
- [Merriam-Webster](https://dictionaryapi.com/) - Dicionário
- [Free Dictionary API](https://dictionaryapi.dev/) - Dicionário público
- [Tatoeba](https://tatoeba.org/) - Frases de exemplo
- [Quotable](https://github.com/lukePeavey/quotable) - Citações
- [Gutendex](https://gutendex.com/) - Textos do Projeto Gutenberg
- [MyMemory](https://mymemory.translated.net/) - Tradução