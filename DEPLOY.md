# Guia de Publicação - Buddy-English

## 🚀 Como Publicar Alterações

O Buddy-English está conectado ao **Streamlit Cloud** e atualiza automaticamente quando você faz push para o GitHub.

### Método 1: Script Automático (Recomendado)

```bash
# No terminal, na pasta do projeto:
deploy.bat "Sua mensagem de commit aqui"
```

Se não passar mensagem, será usada uma automática com data/hora.

### Método 2: Comandos Manuais

```bash
git add .
git commit -m "Descrição das alterações"
git push origin master
```

### Método 3: Via VS Code

1. **Source Control** (Ctrl+Shift+G)
2. Digite a mensagem de commit
3. Clique em **Commit** → **Sync Changes** (seta para cima)

## ⏱️ Tempo de Atualização

- **GitHub**: Imediato
- **Streamlit Cloud**: 1-3 minutos após o push

## 🔗 URLs Úteis

- **Repositório GitHub**: https://github.com/Alexandredd/Buddy-English
- **App Streamlit**: https://buddy-english.streamlit.app/

## 📝 Arquivos Principais

- `app.py` - Aplicação principal
- `requirements.txt` - Dependências Python
- `.streamlit/config.toml` - Configurações do Streamlit

## ⚠️ Atenção

- O Streamlit detecta alterações automaticamente
- Não é necessário fazer deploy manual no Streamlit
- Certifique-se de que `requirements.txt` está atualizado se adicionar novas dependências