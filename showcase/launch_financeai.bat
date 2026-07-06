@echo off
cd /d "C:\Users\ingev\repos\financeai"
start "FinanceAI" "%ProgramFiles%\Git\git-bash.exe" --cd="C:\Users\ingev\repos\financeai\showcase" -c "cd /c/Users/ingev/repos/financeai && financeai interactive; exec bash"
