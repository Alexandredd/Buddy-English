@echo off
echo ========================================
echo Buddy-English - Deploy Automático
echo ========================================
echo.

REM Verifica se há mensagens de commit
if "%1"=="" (
    set COMMIT_MSG=Atualizacao automatica - %date% %time%
) else (
    set COMMIT_MSG=%1
)

echo Adicionando arquivos...
git add .

echo.
echo Commitando: %COMMIT_MSG%
git commit -m "%COMMIT_MSG%"

if %errorlevel% neq 0 (
    echo Nenhuma alteracao para commitar ou erro no commit.
    goto :eof
)

echo.
echo Enviando para GitHub...
git push origin master

if %errorlevel% neq 0 (
    echo Erro ao enviar para GitHub. Verifique sua conexao.
    goto :eof
)

echo.
echo ========================================
echo Deploy concluido!
echo O Streamlit Cloud ira atualizar automaticamente.
echo Acesse: https://buddy-english.streamlit.app/
echo ========================================