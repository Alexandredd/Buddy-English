import urllib.request

# Buscar versão do GitHub
url = 'https://raw.githubusercontent.com/Alexandredd/Buddy-English/master/app.py'
github_content = urllib.request.urlopen(url).read().decode('utf-8')

# Ler versão local
with open('C:/Users/alexa/Desktop/Buddy-English/app.py', 'r', encoding='utf-8') as f:
    local_content = f.read()

# Comparar
if github_content == local_content:
    print("[OK] As versoes sao IGUAIS")
    print("\nSuas alteracoes de hoje NAO estao no GitHub.")
else:
    print("[DIFERENTE] As versoes sao DIFERENTES")
    print("\n=== TAMANHOS ===")
    print(f"GitHub: {len(github_content)} caracteres")
    print(f"Local: {len(local_content)} caracteres")
    
    # Encontrar diferenças
    github_lines = github_content.split('\n')
    local_lines = local_content.split('\n')
    
    print(f"\nGitHub: {len(github_lines)} linhas")
    print(f"Local: {len(local_lines)} linhas")
    
    if len(github_lines) != len(local_lines):
        print(f"\nDiferenca de {abs(len(github_lines) - len(local_lines))} linhas")
