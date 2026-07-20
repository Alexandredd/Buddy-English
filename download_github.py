import urllib.request

# Buscar versão do GitHub
url = 'https://raw.githubusercontent.com/Alexandredd/Buddy-English/master/app.py'
github_content = urllib.request.urlopen(url).read().decode('utf-8')

# Salvar no arquivo local
with open('C:/Users/alexa/Desktop/Buddy-English/app.py', 'w', encoding='utf-8') as f:
    f.write(github_content)

print("[OK] Arquivo app.py atualizado com a versao do GitHub!")
print(f"Total: {len(github_content)} caracteres")
print(f"Linhas: {len(github_content.split(chr(10)))}")