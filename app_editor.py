import streamlit as st
import os

# Configuração da página
st.set_page_config(page_title="Buddy-English Editor", layout="wide")

# Título
st.title("📝 Buddy-English Editor")
st.markdown("---")

# Inicializar o código padrão se não existir
default_code = '''import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Buddy-English", page_icon="🇬🇧")

# Título principal
st.title("🇬🇧 Buddy-English")
st.subheader("Seu assistente de aprendizado de inglês")

# Sidebar com navegação
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Home", "Lições", "Vocabulário", "Quiz"])

# Páginas
if page == "Home":
    st.header("Bem-vindo ao Buddy-English!")
    st.write("Aprenda inglês de forma interativa e divertida.")
    
    # Data atual
    st.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

elif page == "Lições":
    st.header("📚 Lições")
    lesson = st.selectbox("Escolha uma lição:", 
                          ["Presente Simples", "Passado Simples", "Futuro"])
    
    if lesson == "Presente Simples":
        st.write("**Presente Simples** é usado para ações habituais.")
        st.code("I play football every weekend.")
    
    elif lesson == "Passado Simples":
        st.write("**Passado Simples** é usado para ações concluídas no passado.")
        st.code("I played football yesterday.")
    
    else:
        st.write("**Futuro** é usado para ações que ainda vão acontecer.")
        st.code("I will play football tomorrow.")

elif page == "Vocabulário":
    st.header("📖 Vocabulário")
    
    word = st.text_input("Digite uma palavra em inglês:")
    if word:
        st.write(f"**Palavra:** {word}")
        st.write("**Tradução:** (adicione aqui)")
        st.write("**Exemplo:** (adicione aqui)")

else:  # Quiz
    st.header("❓ Quiz")
    
    question = st.radio(
        "Qual é a tradução de 'Hello'?",
        ["Olá", "Tchau", "Bom dia", "Boa noite"]
    )
    
    if st.button("Verificar"):
        if question == "Olá":
            st.success("✅ Correto!")
        else:
            st.error("❌ Incorreto. A resposta é 'Olá'")

# Footer
st.markdown("---")
st.markdown("💡 Desenvolvido com Streamlit")
'''

# Carregar código salvo anteriormente se existir
if 'code' not in st.session_state:
    st.session_state.code = default_code

# Layout com duas colunas
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Editor de Código")
    
    # Área de texto para edição
    edited_code = st.text_area(
        "Edite seu código Python aqui:",
        value=st.session_state.code,
        height=600,
        key="code_editor"
    )
    
    # Botões de ação
    col_save, col_run, col_reset = st.columns(3)
    
    with col_save:
        if st.button("💾 Salvar"):
            st.session_state.code = edited_code
            with open("app.py", "w", encoding="utf-8") as f:
                f.write(edited_code)
            st.success("Código salvo com sucesso!")
    
    with col_run:
        if st.button("▶️ Executar"):
            st.session_state.code = edited_code
            st.info("Para executar o app, use o comando: `streamlit run app.py`")
    
    with col_reset:
        if st.button("🔄 Resetar"):
            st.session_state.code = default_code
            st.rerun()

with col2:
    st.header("Preview do App")
    
    # Mostrar estatísticas do código
    lines = edited_code.count('\n')
    chars = len(edited_code)
    
    st.metric("Linhas de código", lines)
    st.metric("Caracteres", chars)
    
    st.markdown("---")
    
    # Instruções
    st.subheader("📋 Como usar:")
    st.markdown("""
    1. **Edite** o código no painel à esquerda
    2. **Salve** clicando no botão "Salvar"
    3. **Execute** com o comando:
       ```
       streamlit run app.py
       ```
    4. O app abrirá em `http://localhost:8501`
    """)
    
    st.markdown("---")
    
    # Dicas
    st.subheader("💡 Dicas:")
    st.markdown("""
    - Use `st.write()` para texto
    - Use `st.button()` para botões
    - Use `st.text_input()` para campos de texto
    - Use `st.columns()` para layout em colunas
    """)

# Rodapé
st.markdown("---")
st.markdown("🎓 Buddy-English Editor v1.0")