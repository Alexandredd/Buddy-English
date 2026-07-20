#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buddy-English - Versão Terminal/CLI
Visualização do app em modo texto no terminal
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  BUDDY-ENGLISH - Versao Terminal{Colors.END}")
    print(f"{Colors.HEADER}{'='*70}{Colors.END}")
    print()

def print_home():
    print(f"{Colors.GREEN}🏠 HOME{Colors.END}")
    print(f"{Colors.CYAN}Aprenda inglês de forma interativa e divertida.{Colors.END}")
    print(f"{Colors.YELLOW}📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}{Colors.END}")
    print()

def print_lessons():
    print(f"{Colors.GREEN}📚 LIÇÕES DE INGLÊS{Colors.END}")
    print()
    
    lessons = [
        ("1", "Presente Simples", "Ações habituais", "I play football every weekend."),
        ("2", "Passado Simples", "Ações concluídas", "I played football yesterday."),
        ("3", "Futuro", "Ações futuras", "I will play football tomorrow.")
    ]
    
    for num, title, desc, example in lessons:
        print(f"{Colors.YELLOW}[{num}]{Colors.END} {Colors.BOLD}{title}{Colors.END}")
        print(f"    {desc}")
        print(f"    {Colors.CYAN}Exemplo: {example}{Colors.END}")
        print()

def print_vocabulary():
    print(f"{Colors.GREEN}📖 VOCABULÁRIO{Colors.END}")
    print()
    print(f"{Colors.CYAN}Digite uma palavra em inglês para ver a tradução{Colors.END}")
    print()

def print_quiz():
    print(f"{Colors.GREEN}❓ QUIZ INTERATIVO{Colors.END}")
    print()
    print(f"{Colors.YELLOW}Pergunta:{Colors.END} Qual é a tradução de 'Hello'?")
    print()
    print(f"  {Colors.CYAN}[1]{Colors.END} Olá")
    print(f"  {Colors.CYAN}[2]{Colors.END} Tchau")
    print(f"  {Colors.CYAN}[3]{Colors.END} Bom dia")
    print(f"  {Colors.CYAN}[4]{Colors.END} Boa noite")
    print()
    print(f"{Colors.GREEN}Resposta correta: [1] Olá{Colors.END}")
    print()

def print_menu():
    print(f"{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}MENU PRINCIPAL{Colors.END}")
    print(f"{Colors.HEADER}{'='*70}{Colors.END}")
    print()
    print(f"  {Colors.CYAN}[1]{Colors.END} Home")
    print(f"  {Colors.CYAN}[2]{Colors.END} Licoes")
    print(f"  {Colors.CYAN}[3]{Colors.END} Vocabulario")
    print(f"  {Colors.CYAN}[4]{Colors.END} Quiz")
    print(f"  {Colors.CYAN}[0]{Colors.END} Sair")
    print()

def main():
    while True:
        print_header()
        print_menu()
        
        try:
            choice = input(f"{Colors.YELLOW}Escolha uma opção: {Colors.END}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.RED}Encerrando...{Colors.END}")
            break
        
        print()
        
        if choice == '1':
            print_home()
        elif choice == '2':
            print_lessons()
        elif choice == '3':
            print_vocabulary()
        elif choice == '4':
            print_quiz()
        elif choice == '0':
            print(f"{Colors.GREEN}Ate logo!{Colors.END}")
            break
        else:
            print(f"{Colors.RED}Opção inválida! Tente novamente.{Colors.END}")
        
        input(f"\n{Colors.CYAN}Pressione ENTER para continuar...{Colors.END}")

if __name__ == "__main__":
    print(f"{Colors.GREEN}Iniciando Buddy-English - Versão Terminal...{Colors.END}")
    print()
    main()