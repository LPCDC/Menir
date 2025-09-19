@echo off
setlocal enabledelayedexpansion

echo ====================================
echo Gatilhos disponíveis:
echo ====================================

powershell -NoProfile -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; $map=Get-Content 'triggers.json' | ConvertFrom-Json; $i=1; foreach ($k in $map.PSObject.Properties.Name) { Write-Output ($i.ToString() + '. ' + $k); $i++ }"

set /p choice="Digite o numero do gatilho desejado: "

powershell -NoProfile -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; $map=Get-Content 'triggers.json' | ConvertFrom-Json; $keys = $map.PSObject.Properties.Name; $index = %choice% - 1; if ($index -ge 0 -and $index -lt $keys.Count) { $k = $keys[$index]; $file = $map.$k; if (Test-Path $file) { Start-Process notepad $file } if ($k -ieq 'Gatomia') { foreach ($proj in @('projects\\Itau\\Itau.md','projects\\Renderizador\\Renderizador.md','projects\\Imoveis\\Imoveis.md','projects\\Textos\\Textos.md')) { if (Test-Path $proj) { Start-Process notepad $proj } } } } else { Write-Output 'Opcao invalida.' }"

pause
