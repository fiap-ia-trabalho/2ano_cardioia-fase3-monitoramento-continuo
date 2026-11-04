@echo off
cd /d "%~dp0node-red"
if not exist node_modules (
  echo Preparando o dashboard pela primeira vez...
  call npm ci
  if errorlevel 1 ( pause & exit /b 1 )
)
echo Dashboard: http://127.0.0.1:1880/dashboard/monitoramento
echo Para encerrar, pressione Ctrl+C nesta janela.
call npm start
pause
