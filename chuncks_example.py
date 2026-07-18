#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso do modulo chuncks.py
Demonstra todas as funcionalidades disponiveis.
"""

import sys
import os
import random

# Adiciona o diretorio atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chuncks


def print_section(title):
    """Imprime secao formatada."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_basic_usage():
    """Exemplo 1: Uso basico - Listar e filtrar chunks."""
    print_section("EXEMPLO 1: Uso Basico - Listar e Filtrar Chunks")
    
    # Inicializa modulo
    status = chuncks.initialize_module()
    print(f"\n[OK] Modulo inicializado: {status['status']}")
    print(f"  Total de chunks: {status['total_chunks']}")
    print(f"  Chunks base: {status['base_chunks']}")
    print(f"  Chunks customizados: {status['custom_chunks']}")
    print(f"  Contextos disponiveis: {', '.join(status['contexts'])}")
    
    # Lista todos os contextos
    print("\n--- Contextos Disponiveis ---")
    contexts = chuncks.list_contexts()
    for i, context in enumerate(contexts, 1):
        print(f"  {i}. {context}")
    
    # Filtra por contexto
    print("\n--- Chunks de 'Conversacao Basica' ---")
    basic_chunks = chuncks.filter_chunks(context="Conversacao Basica")
    for chunk in basic_chunks:
        print(f"  * {chunk['content']}")
        print(f"    Traducao: {chunk['translation']}")
        print(f"    Dificuldade: {chunk['difficulty']}")
        print()
    
    # Filtra por dificuldade
    print("\n--- Chunks Iniciantes (beginner) ---")
    beginner_chunks = chuncks.get_chunks_by_difficulty("beginner")
    for chunk in beginner_chunks[:3]:
        print(f"  * {chunk['content']} ({chunk['context']})")
    
    # Busca por texto
    print("\n--- Busca: 'meeting' ---")
    results = chuncks.search_chunks("meeting")
    for chunk in results:
        print(f"  * {chunk['content']}")


def example_2_add_chunks():
    """Exemplo 2: Adicionar chunks manualmente."""
    print_section("EXEMPLO 2: Adicionar Chunks Manualmente")
    
    # Adiciona um chunk unico
    new_chunk = {
        "context": "Saude",
        "content": "I don't feel well today.",
        "translation": "Nao me sinto bem hoje.",
        "when_to_use": "Quando esta doente ou nao se sente bem.",
        "difficulty": "beginner",
        "tags": ["health", "sick", "daily"],
        "examples": "I don't feel well today. I think I have a fever."
    }
    
    success, message = chuncks.add_chunk(new_chunk)
    print(f"\nAdicionar chunk unico: {'[OK]' if success else '[ERRO]'}")
    print(f"  Mensagem: {message}")
    
    # Adiciona multiplos chunks em lote
    print("\n--- Adicionando multiplos chunks ---")
    batch_chunks = [
        {
            "context": "Educacao",
            "content": "Could you explain this again?",
            "translation": "Voce poderia explicar isso de novo?",
            "when_to_use": "Em sala de aula quando nao entendeu algo.",
            "difficulty": "beginner",
            "tags": ["education", "classroom", "learning"]
        },
        {
            "context": "Educacao",
            "content": "What's the homework for today?",
            "translation": "Qual e a licao de casa para hoje?",
            "when_to_use": "Ao perguntar sobre tarefas escolares.",
            "difficulty": "beginner",
            "tags": ["education", "homework", "school"]
        },
        {
            "context": "Saude",
            "content": "I need to see a doctor.",
            "translation": "Preciso ver um medico.",
            "when_to_use": "Quando precisa de atendimento medico.",
            "difficulty": "beginner",
            "tags": ["health", "doctor", "emergency"]
        },
        {
            "context": "Saude",
            "content": "I don't feel well today.",
            "translation": "Nao me sinto bem hoje.",
            "when_to_use": "Quando esta doente.",
            "difficulty": "beginner"
        },
        {
            "context": "Teste",
            "content": "Test content",
            "when_to_use": "Teste"
        }
    ]
    
    stats = chuncks.add_chunks_bulk(batch_chunks)
    print(f"  Adicionados: {stats['added']}")
    print(f"  Duplicados: {stats['duplicates']}")
    print(f"  Invalidos: {stats['invalid']}")
    
    # Mostra total atual
    total = chuncks.get_chunk_count()
    print(f"\n  Total de chunks agora: {total}")


def example_3_file_upload():
    """Exemplo 3: Upload de chunks via arquivo JSON e CSV."""
    print_section("EXEMPLO 3: Upload de Arquivos (JSON e CSV)")
    
    # Exemplo de JSON
    json_content = """[
        {
            "context": "Tecnologia",
            "content": "The software update is ready to install.",
            "translation": "A atualizacao de software esta pronta para instalar.",
            "when_to_use": "Ao notificar sobre atualizacoes de programas.",
            "difficulty": "intermediate",
            "tags": ["technology", "software", "updates"],
            "examples": "The software update is ready to install. Restart your computer."
        },
        {
            "context": "Tecnologia",
            "content": "Could you help me with this app?",
            "translation": "Voce poderia me ajudar com este aplicativo?",
            "when_to_use": "Ao pedir suporte tecnico.",
            "difficulty": "beginner",
            "tags": ["technology", "help", "support"]
        }
    ]"""
    
    print("\n--- Upload via JSON ---")
    stats = chuncks.upload_chunks_from_file(json_content, file_format="json")
    print(f"  Adicionados: {stats['added']}")
    print(f"  Duplicados: {stats['duplicates']}")
    print(f"  Invalidos: {stats['invalid']}")
    
    # Exemplo de CSV
    csv_content = """context,content,translation,when_to_use,difficulty,tags,examples
Musica,Do you like this song?,Voce gosta dessa musica?,Perguntar sobre preferencia musical,beginner,music,preferences,Do you like this song? Yes, it's my favorite.
Musica,I play the guitar.,Eu toco guitarra.,Falar sobre hobbies musicais,beginner,music,hobbies,I play the guitar. Since I was 10 years old.
Cinema,What movie are we watching?,Que filme vamos assistir?,Ao escolher um filme,beginner,cinema,entertainment,What movie are we watching? Let's watch a comedy."""
    
    print("\n--- Upload via CSV ---")
    stats = chuncks.upload_chunks_from_file(csv_content, file_format="csv")
    print(f"  Adicionados: {stats['added']}")
    print(f"  Duplicados: {stats['duplicates']}")
    print(f"  Invalidos: {stats['invalid']}")
    
    # Valida arquivo antes do upload
    print("\n--- Validacao de Arquivo ---")
    validation = chuncks.validate_chunks_file(json_content, "json")
    print(f"  Valido: {validation['valid']}")
    print(f"  Total: {validation['total']}")
    print(f"  Validos: {validation['valid_chunks']}")
    if validation['errors']:
        print(f"  Erros: {validation['errors']}")


def example_4_online_chunks():
    """Exemplo 4: Receber chunks online com contexto."""
    print_section("EXEMPLO 4: Receber Chunks Online")
    
    # Busca chunks online
    print("\n--- Buscando chunks online (com cache) ---")
    online_chunks = chuncks.fetch_online_chunks(limit=3)
    
    if online_chunks:
        print(f"  Encontrados {len(online_chunks)} chunks online:\n")
        for chunk in online_chunks:
            print(f"  Contexto: {chunk['context']}")
            print(f"  Conteudo: {chunk['content']}")
            print(f"  Quando usar: {chunk['when_to_use']}")
            print(f"  Tags: {', '.join(chunk['tags'])}")
            print()
    else:
        print("  Nenhum chunk online disponivel no momento.")
    
    # Informacoes do cache
    print("\n--- Informacoes do Cache Online ---")
    cache_info = chuncks.get_online_cache_info()
    print(f"  Status: {cache_info['status']}")
    print(f"  Ultima atualizacao: {cache_info['updated_at']}")
    print(f"  Chunks em cache: {cache_info['count']}")
    
    # Incorpora chunks online automaticamente
    print("\n--- Incorporando chunks online ---")
    added = chuncks.incorporate_online_chunks(limit=2)
    print(f"  Chunks adicionados: {added}")


def example_5_download_export():
    """Exemplo 5: Download e exportacao de chunks."""
    print_section("EXEMPLO 5: Download e Exportacao")
    
    # Exporta todos em JSON
    print("\n--- Exportar todos os chunks (JSON) ---")
    json_export = chuncks.export_chunks_json()
    print(f"  Tamanho: {len(json_export)} caracteres")
    print(f"  Primeiros 200 chars: {json_export[:200]}...")
    
    # Exporta todos em CSV
    print("\n--- Exportar todos os chunks (CSV) ---")
    csv_export = chuncks.export_chunks_csv()
    print(f"  Tamanho: {len(csv_export)} caracteres")
    print(f"  Primeiras 3 linhas:")
    for i, line in enumerate(csv_export.split('\n')[:3]):
        print(f"    {line}")
    
    # Exporta por contexto
    print("\n--- Exportar chunks de 'Conversação Básica' ---")
    context_export = chuncks.export_chunks_by_context("Conversação Básica")
    print(f"  Tamanho: {len(context_export)} caracteres")
    
    # Salva em arquivo (exemplo)
    print("\n--- Salvando em arquivos ---")
    try:
        # JSON
        with open("chuncks_export.json", "w", encoding="utf-8") as f:
            f.write(json_export)
        print("  [OK] Salvo: chuncks_export.json")
        
        # CSV
        with open("chuncks_export.csv", "w", encoding="utf-8") as f:
            f.write(csv_export)
        print("  [OK] Salvo: chuncks_export.csv")
        
        # Por contexto
        with open("chuncks_conversacao.json", "w", encoding="utf-8") as f:
            f.write(context_export)
        print("  [OK] Salvo: chuncks_conversacao.json")
    except Exception as e:
        print(f"  [ERRO] Erro ao salvar: {e}")


def example_6_study_features():
    """Exemplo 6: Funcionalidades de estudo."""
    print_section("EXEMPLO 6: Funcionalidades de Estudo")
    
    # Registra sessoes de estudo
    print("\n--- Registrando Sessoes de Estudo ---")
    chunks_to_study = chuncks.get_random_chunks(limit=3)
    
    for chunk in chunks_to_study:
        success = random.choice([True, True, False])
        time_spent = random.uniform(5, 30)
        
        chuncks.record_study_session(chunk["id"], success, time_spent)
        print(f"  * {chunk['content'][:50]}...")
        print(f"    Resultado: {'[OK] Acertou' if success else '[ERRO] Errou'}")
        print(f"    Tempo: {time_spent:.1f}s")
    
    # Estatisticas de estudo
    print("\n--- Estatisticas de Estudo ---")
    stats = chuncks.get_study_statistics()
    print(f"  Total de chunks: {stats['total_chunks']}")
    print(f"  Chunks estudados: {stats['studied_chunks']}")
    print(f"  Nao estudados: {stats['not_studied']}")
    print(f"  Total de revisoes: {stats['total_reviews']}")
    print(f"  Taxa de sucesso: {stats['success_rate']}%")
    print(f"  Tempo total: {stats['total_time_minutes']} minutos")
    print(f"  Para revisar hoje: {stats['chunks_to_review_today']}")
    
    print("\n  Distribuicao por dificuldade:")
    for diff, count in stats['difficulty_distribution'].items():
        print(f"    {diff}: {count}")
    
    print("\n  Distribuicao por contexto:")
    for ctx, count in stats['context_distribution'].items():
        print(f"    {ctx}: {count}")
    
    # Fila de estudo
    print("\n--- Fila de Estudo (Spaced Repetition) ---")
    study_queue = chuncks.get_study_queue(limit=5)
    for i, chunk in enumerate(study_queue, 1):
        print(f"  {i}. {chunk['content'][:60]}... ({chunk['difficulty']})")
    
    # Chunks para revisar
    print("\n--- Chunks para Revisar Hoje ---")
    to_review = chuncks.get_chunks_to_review()
    if to_review:
        for chunk, progress in to_review[:5]:
            print(f"  * {chunk['content'][:50]}...")
            print(f"    Revisoes: {progress.get('reviews', 0)}, Sucessos: {progress.get('successes', 0)}")
    else:
        print("  Nenhum chunk para revisar hoje!")
    
    # Insights de aprendizado
    print("\n--- Insights de Aprendizado ---")
    insights = chuncks.get_learning_insights()
    
    if insights['recommendations']:
        print("  Recomendacoes:")
        for rec in insights['recommendations']:
            print(f"    * {rec}")
    
    if insights['difficult_chunks']:
        print("\n  Chunks Dificeis:")
        for chunk in insights['difficult_chunks'][:3]:
            print(f"    * {chunk['content'][:50]}... ({chunk['success_rate']}% sucesso)")
    
    if insights['mastered_chunks']:
        print("\n  Chunks Dominados:")
        for content in insights['mastered_chunks'][:3]:
            print(f"    [OK] {content[:50]}...")
    
    print(f"\n  Sequencia de estudos: {insights['streak_days']} dias")


def example_7_quiz_and_flashcards():
    """Exemplo 7: Gerar quizzes e flashcards."""
    print_section("EXEMPLO 7: Quizzes e Flashcards")
    
    # Gera flashcards
    print("\n--- Flashcards de Estudo ---")
    flashcards = chuncks.generate_study_flashcards(limit=5)
    for i, card in enumerate(flashcards, 1):
        print(f"\n  Flashcard {i}:")
        print(f"    Frente: {card['front']}")
        print(f"    Verso: {card['back']}")
        print(f"    Contexto: {card['context']}")
        print(f"    Quando usar: {card['when_to_use']}")
    
    # Gera quiz
    print("\n--- Quiz de Traducao ---")
    quiz = chuncks.generate_quiz_questions(limit=3)
    for i, question in enumerate(quiz, 1):
        print(f"\n  Pergunta {i}: {question['question']}")
        for j, option in enumerate(question['options'], 1):
            print(f"    [{j}] {option}")
        print(f"    Resposta correta: {question['correct_answer']}")
        print(f"    Explicacao: {question['explanation']}")


def example_8_integration():
    """Exemplo 8: Integracao com outros modulos."""
    print_section("EXEMPLO 8: Integracao com Outros Modulos")
    
    # Sugestoes por contexto
    print("\n--- Sugestoes para Contexto 'Restaurante' ---")
    suggestions = chuncks.get_chunks_suggestions_for_context("Restaurante", limit=5)
    for chunk in suggestions:
        print(f"  * {chunk['content']}")
        print(f"    {chunk['translation']}")
    
    # Chunks por tag
    print("\n--- Chunks com tag 'business' ---")
    business_chunks = chuncks.get_chunks_by_tag("business")
    for chunk in business_chunks:
        print(f"  * {chunk['content']} ({chunk['context']})")
    
    # Chunks aleatorios
    print("\n--- 5 Chunks Aleatorios ---")
    random_chunks = chuncks.get_random_chunks(limit=5)
    for chunk in random_chunks:
        print(f"  * {chunk['content'][:50]}... [{chunk['difficulty']}]")


def example_9_delete_and_reset():
    """Exemplo 9: Deletar e resetar dados."""
    print_section("EXEMPLO 9: Deletar e Resetar")
    
    # Adiciona chunk temporario
    temp_chunk = {
        "context": "Teste",
        "content": "This is a test chunk.",
        "translation": "Este e um chunk de teste.",
        "difficulty": "beginner"
    }
    
    success, message = chuncks.add_chunk(temp_chunk)
    print(f"\nAdicionando chunk temporario: {'[OK]' if success else '[ERRO]'}")
    
    if success:
        # Busca o chunk
        chunks = chuncks.search_chunks("test chunk")
        if chunks:
            chunk_id = chunks[0]["id"]
            print(f"  ID do chunk: {chunk_id}")
            
            # Deleta
            deleted = chuncks.delete_chunk(chunk_id)
            print(f"  Deletar chunk: {'[OK]' if deleted else '[ERRO]'}")
    
    # Reset de progresso (cuidado!)
    print("\n--- Reset de Progresso de Estudo ---")
    print("  [AVISO] Esta operacao limpa todo o progresso de estudo!")
    print("     (Nao executado automaticamente no exemplo)")
    
    # Para resetar, descomente a linha abaixo:
    # chuncks.reset_study_progress()


def main():
    """Executa todos os exemplos."""
    print("\n")
    print("=" * 70)
    print("  MODULO CHUNCKS - EXEMPLOS DE USO")
    print("=" * 70)
    
    try:
        example_1_basic_usage()
        example_2_add_chunks()
        example_3_file_upload()
        example_4_online_chunks()
        example_5_download_export()
        example_6_study_features()
        example_7_quiz_and_flashcards()
        example_8_integration()
        example_9_delete_and_reset()
        
        print_section("EXEMPLOS CONCLUIDOS")
        print("\n[TODOS] Todos os exemplos foram executados com sucesso!")
        print("  Verifique os arquivos gerados:")
        print("    - chuncks_export.json")
        print("    - chuncks_export.csv")
        print("    - chuncks_conversacao.json")
        print()
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante execucao: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()