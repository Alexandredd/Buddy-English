# Módulo Chuncks - Sistema de Aprendizado de Inglês

## 📚 Visão Geral

O módulo `chuncks.py` é um sistema completo de gerenciamento de pedaços de conteúdo (chunks) para aprendizado de inglês, desenvolvido para o projeto Buddy-English. Ele oferece funcionalidades avançadas de estudo com repetição espaçada, upload/download de conteúdo e integração com APIs online.

## ✨ Funcionalidades Principais

### 1. **Gerenciamento de Chunks**
- ✅ Base de dados com 8 chunks pré-carregados
- ✅ Adicionar chunks manualmente (único ou em lote)
- ✅ Filtrar por contexto, dificuldade e tags
- ✅ Busca textual em conteúdo, tradução e contexto
- ✅ Remover chunks customizados
- ✅ Proteção de chunks base (não editáveis)

### 2. **Upload de Arquivos**
- ✅ Suporte a formato JSON
- ✅ Suporte a formato CSV
- ✅ Validação automática de arquivos
- ✅ Detecção de duplicatas e inválidos
- ✅ Estatísticas de upload (adicionados, duplicados, inválidos)

### 3. **Download e Exportação**
- ✅ Exportar todos os chunks em JSON
- ✅ Exportar todos os chunks em CSV
- ✅ Exportar chunks por contexto específico
- ✅ Arquivos com encoding UTF-8

### 4. **Recepção Online**
- ✅ Busca de frases autênticas em APIs públicas
- ✅ Sistema de cache inteligente (24h)
- ✅ Incorporação automática de chunks online
- ✅ Informações de cache (status, data, contagem)

### 5. **Sistema de Estudo Avançado**
- ✅ **Repetição Espaçada (Spaced Repetition)** - algoritmo SM-2 simplificado
- ✅ Registro de sessões de estudo (sucesso/falha, tempo gasto)
- ✅ Estatísticas completas (taxa de sucesso, tempo total, etc.)
- ✅ Fila de estudo priorizada
- ✅ Cálculo de streak (dias consecutivos)
- ✅ Identificação de chunks difíceis e dominados

### 6. **Ferramentas de Estudo**
- ✅ **Flashcards** - geração aleatória para estudo
- ✅ **Quizzes** - perguntas de múltipla escolha
- ✅ Insights personalizados de aprendizado
- ✅ Recomendações automáticas

### 7. **Integração**
- ✅ Funções de sugestão por contexto
- ✅ Compatível com outros módulos do Buddy-English
- ✅ API simples e intuitiva

## 📦 Estrutura de Dados

### Formato de Chunk

```python
{
    "id": "chunk_001",                    # ID único
    "context": "Conversação Básica",       # Contexto de uso
    "content": "How are you doing today?", # Frase em inglês
    "translation": "Como você está hoje?", # Tradução
    "when_to_use": "Cumprimento informal", # Quando usar
    "difficulty": "beginner",              # beginner/intermediate/advanced
    "tags": ["greeting", "daily"],         # Tags para filtros
    "examples": "Pretty good, thanks!",    # Exemplos de uso
    "created_at": "2024-01-01T00:00:00Z"  # Data de criação
}
```

### Campos Obrigatórios
- `context` - Contexto onde a frase é usada
- `content` - Frase em inglês
- `translation` - Tradução em português

### Campos Opcionais
- `when_to_use` - Instruções de uso
- `difficulty` - Nível de dificuldade
- `tags` - Lista de tags para organização
- `examples` - Exemplos práticos
- `created_at` - Data de criação (gerado automaticamente)

## 🚀 Uso Básico

### Inicialização

```python
import chuncks

# Inicializa o módulo
status = chuncks.initialize_module()
print(f"Total de chunks: {status['total_chunks']}")
print(f"Contextos: {status['contexts']}")
```

### Listar e Filtrar Chunks

```python
# Lista todos os contextos
contexts = chuncks.list_contexts()

# Filtra por contexto
chunks = chuncks.filter_chunks(context="Conversação Básica")

# Filtra por dificuldade
beginner = chuncks.get_chunks_by_difficulty("beginner")

# Busca textual
results = chuncks.search_chunks("meeting")

# Chunks aleatórios
random_chunks = chuncks.get_random_chunks(limit=5)
```

### Adicionar Chunks

```python
# Adiciona um chunk único
new_chunk = {
    "context": "Saúde",
    "content": "I don't feel well today.",
    "translation": "Não me sinto bem hoje.",
    "when_to_use": "Quando está doente.",
    "difficulty": "beginner",
    "tags": ["health", "daily"]
}

success, message = chuncks.add_chunk(new_chunk)

# Adiciona múltiplos chunks
batch = [chunk1, chunk2, chunk3]
stats = chuncks.add_chunks_bulk(batch)
print(f"Adicionados: {stats['added']}")
print(f"Duplicados: {stats['duplicates']}")
print(f"Inválidos: {stats['invalid']}")
```

### Upload de Arquivos

```python
# Upload via JSON
with open("chunks.json", "r", encoding="utf-8") as f:
    content = f.read()

stats = chuncks.upload_chunks_from_file(content, file_format="json")

# Upload via CSV
with open("chunks.csv", "r", encoding="utf-8") as f:
    content = f.read()

stats = chuncks.upload_chunks_from_file(content, file_format="csv")

# Valida antes de enviar
validation = chuncks.validate_chunks_file(content, "json")
if validation['valid']:
    print(f"Válidos: {validation['valid_chunks']}/{validation['total']}")
```

### Download e Exportação

```python
# Exporta todos em JSON
json_data = chuncks.export_chunks_json()
with open("export.json", "w", encoding="utf-8") as f:
    f.write(json_data)

# Exporta todos em CSV
csv_data = chuncks.export_chunks_csv()
with open("export.csv", "w", encoding="utf-8") as f:
    f.write(csv_data)

# Exporta por contexto
context_data = chuncks.export_chunks_by_context("Restaurante")
```

### Chunks Online

```python
# Busca chunks online (com cache)
online_chunks = chuncks.fetch_online_chunks(limit=5)

# Força atualização do cache
fresh_chunks = chuncks.fetch_online_chunks(limit=5, force_refresh=True)

# Incorpora automaticamente
added = chuncks.incorporate_online_chunks(limit=3)

# Informações do cache
cache_info = chuncks.get_online_cache_info()
print(f"Status: {cache_info['status']}")
print(f"Chunks em cache: {cache_info['count']}")
```

### Sistema de Estudo

```python
# Registra sessão de estudo
chuncks.record_study_session(
    chunk_id="chunk_001",
    success=True,  # Acertou
    time_spent=15.5  # Segundos
)

# Estatísticas
stats = chuncks.get_study_statistics()
print(f"Taxa de sucesso: {stats['success_rate']}%")
print(f"Tempo total: {stats['total_time_minutes']} minutos")
print(f"Para revisar hoje: {stats['chunks_to_review_today']}")

# Fila de estudo (spaced repetition)
study_queue = chuncks.get_study_queue(limit=10)

# Chunks para revisar hoje
to_review = chuncks.get_chunks_to_review()

# Insights de aprendizado
insights = chuncks.get_learning_insights()
print(f"Streak: {insights['streak_days']} dias")
for rec in insights['recommendations']:
    print(f"• {rec}")
```

### Flashcards e Quizzes

```python
# Gera flashcards
flashcards = chuncks.generate_study_flashcards(limit=20, context="Todos")
for card in flashcards:
    print(f"Frente: {card['front']}")
    print(f"Verso: {card['back']}")

# Gera quiz
quiz = chuncks.generate_quiz_questions(limit=10)
for question in quiz:
    print(f"Pergunta: {question['question']}")
    for i, option in enumerate(question['options'], 1):
        print(f"  [{i}] {option}")
    print(f"Resposta: {question['correct_answer']}")
```

## 🎯 Recursos de Estudo

### Sistema de Repetição Espaçada

O módulo implementa uma versão simplificada do algoritmo SM-2:

- **Intervalos de revisão**: 1, 3, 7, 14, 21, 30, 45, 60 dias
- **Ajuste automático**: Aumenta intervalo se acertar, diminui se errar
- **Priorização**: Chunks difíceis são revisados mais cedo
- **Streak**: Conta dias consecutivos de estudo

### Estatísticas Disponíveis

```python
stats = chuncks.get_study_statistics()

# Métricas principais
stats['total_chunks']          # Total de chunks
stats['studied_chunks']        # Chunks estudados
stats['not_studied']           # Chunks não estudados
stats['total_reviews']         # Total de revisões
stats['success_rate']          # Taxa de sucesso (%)
stats['total_time_minutes']    # Tempo total de estudo
stats['chunks_to_review_today'] # Revisões pendentes

# Distribuições
stats['difficulty_distribution']  # Por dificuldade
stats['context_distribution']     # Por contexto
```

### Insights de Aprendizado

```python
insights = chuncks.get_learning_insights()

# Chunks difíceis (taxa < 50%)
insights['difficult_chunks']

# Chunks dominados (taxa >= 90%, >= 5 revisões)
insights['mastered_chunks']

# Recomendações personalizadas
insights['recommendations']

# Sequência de estudos
insights['streak_days']
```

## 🔧 Funções Avançadas

### Busca e Filtros

```python
# Busca textual
results = chuncks.search_chunks("restaurant")

# Filtro combinado
chunks = chuncks.filter_chunks(
    context="Restaurante",
    difficulty="beginner",
    tags=["polite", "dining"]
)

# Por tag específica
business = chuncks.get_chunks_by_tag("business")

# Por dificuldade
advanced = chuncks.get_chunks_by_difficulty("advanced")
```

### Integração com Outros Módulos

```python
# Sugestões para um contexto
suggestions = chuncks.get_chunks_suggestions_for_context("Restaurante", limit=5)

# Busca chunk por ID
chunk = chuncks.get_chunk_by_id("chunk_001")

# Contagem total
total = chuncks.get_chunk_count()
```

### Gerenciamento de Dados

```python
# Deletar chunk customizado
deleted = chuncks.delete_chunk("chunk_123456")

# Reset de progresso (todos os chunks)
chuncks.reset_study_progress()

# Reset de progresso (chunk específico)
chuncks.reset_study_progress(chunk_id="chunk_001")
```

## 📊 Arquivos de Dados

O módulo cria os seguintes arquivos automaticamente:

| Arquivo | Descrição |
|---------|-----------|
| `chuncks_data.json` | Chunks customizados (não sobrescreve base) |
| `chuncks_online_cache.json` | Cache de chunks online (24h) |
| `chuncks_study_progress.json` | Progresso de estudo do usuário |

## 🎓 Exemplos de Uso

Consulte o arquivo `chuncks_example.py` para exemplos completos de todas as funcionalidades:

```bash
python chuncks_example.py
```

O exemplo demonstra:
1. Uso básico e filtros
2. Adição de chunks (único e lote)
3. Upload via JSON e CSV
4. Busca de chunks online
5. Exportação e download
6. Sistema de estudo completo
7. Geração de flashcards e quizzes
8. Integração com outros módulos
9. Gerenciamento de dados

## 🔌 Integração com Streamlit

Para usar no app principal (`app.py`):

```python
import chuncks as ck

# Sidebar de chunks
with st.sidebar:
    st.subheader("📚 Chunks de Estudo")
    
    # Filtros
    context = st.selectbox("Contexto", ["Todos"] + ck.list_contexts())
    difficulty = st.selectbox("Dificuldade", ["Todos", "beginner", "intermediate", "advanced"])
    
    # Exibe chunks
    chunks = ck.filter_chunks(context=context, difficulty=difficulty)
    for chunk in chunks:
        with st.expander(chunk['content']):
            st.write(f"**Tradução:** {chunk['translation']}")
            st.write(f"**Quando usar:** {chunk['when_to_use']}")
```

## 🛠️ API Reference

### Gerenciamento de Chunks

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `load_chunks()` | Carrega todos os chunks | `List[Chunk]` |
| `add_chunk(chunk)` | Adiciona um chunk | `tuple[bool, str]` |
| `add_chunks_bulk(chunks)` | Adiciona múltiplos | `Dict[str, int]` |
| `delete_chunk(id)` | Remove um chunk | `bool` |
| `get_chunk_by_id(id)` | Busca por ID | `Optional[Chunk]` |

### Filtros e Busca

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `list_contexts()` | Lista contextos | `List[str]` |
| `filter_chunks(ctx, diff, tags)` | Filtra chunks | `List[Chunk]` |
| `search_chunks(query)` | Busca textual | `List[Chunk]` |
| `get_random_chunks(limit)` | Chunks aleatórios | `List[Chunk]` |
| `get_chunks_by_difficulty(d)` | Por dificuldade | `List[Chunk]` |
| `get_chunks_by_tag(tag)` | Por tag | `List[Chunk]` |

### Upload/Download

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `upload_chunks_from_file(content, fmt)` | Upload de arquivo | `Dict[str, int]` |
| `validate_chunks_file(content, fmt)` | Valida arquivo | `Dict[str, any]` |
| `export_chunks_json()` | Exporta JSON | `str` |
| `export_chunks_csv()` | Exporta CSV | `str` |
| `export_chunks_by_context(ctx)` | Exporta por contexto | `str` |

### Online

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `fetch_online_chunks(limit, force)` | Busca online | `List[Chunk]` |
| `incorporate_online_chunks(limit)` | Incorpora online | `int` |
| `get_online_cache_info()` | Info do cache | `Dict[str, str]` |

### Estudo

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `record_study_session(id, success, time)` | Registra estudo | `None` |
| `get_study_statistics()` | Estatísticas | `Dict` |
| `get_study_queue(limit)` | Fila de estudo | `List[Chunk]` |
| `get_chunks_to_review()` | Para revisar hoje | `List[tuple]` |
| `get_learning_insights()` | Insights | `Dict` |
| `reset_study_progress(id?)` | Reseta progresso | `bool` |

### Ferramentas

| Função | Descrição | Retorno |
|--------|-----------|---------|
| `generate_study_flashcards(limit)` | Gera flashcards | `List[Dict]` |
| `generate_quiz_questions(limit)` | Gera quiz | `List[Dict]` |
| `get_chunks_suggestions_for_context(ctx)` | Sugestões | `List[Chunk]` |
| `initialize_module()` | Inicializa módulo | `Dict[str, any]` |

## 🎨 Características Técnicas

### Performance
- Cache inteligente de chunks online (24h)
- Carregamento lazy de dados
- Processamento em lote para uploads
- Índices em memória para buscas rápidas

### Confiabilidade
- Validação rigorosa de dados
- Tratamento de erros robusto
- Fallbacks para APIs externas
- Proteção de dados base (read-only)

### Usabilidade
- API intuitiva e consistente
- Mensagens de erro claras
- Estatísticas detalhadas
- Insights automáticos de aprendizado

## 📝 Notas de Desenvolvimento

### Decisões de Design

1. **Separação de chunks base e customizados**: Os chunks base são pré-carregados e não podem ser modificados, apenas os customizados são salvos em arquivo.

2. **Sistema de cache online**: Implementado para reduzir chamadas a APIs externas e melhorar performance.

3. **Spaced repetition simplificado**: Usa intervalos fixos baseados no algoritmo SM-2, balanceando simplicidade e eficácia.

4. **Validação em múltiplas camadas**: Arquivos são validados antes do upload, e chunks são normalizados antes de serem salvos.

### Melhorias Futuras

- [ ] Suporte a mais APIs de frases online
- [ ] Exportação em formato Anki (para importação no Anki)
- [ ] Modo offline completo com sync quando online
- [ ] Gráficos de progresso e evolução
- [ ] Sistema de conquistas e gamificação
- [ ] Compartilhamento de chunks entre usuários
- [ ] Suporte a áudio nativo (TTS)
- [ ] Modo escuro/claro na interface
- [ ] Backup automático na nuvem
- [ ] Análise de erros mais detalhada

## 📄 Licença

Parte do projeto Buddy-English.

## 👨‍💻 Autor

Desenvolvido para o projeto Buddy-English - Sistema de aprendizado de inglês interativo.