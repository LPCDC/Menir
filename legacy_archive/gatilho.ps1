param(
    [string]$trigger
)

# Lê gatilhos
$map = Get-Content "triggers.json" | ConvertFrom-Json

if (-not $trigger) {
    Write-Host "📌 Gatilhos disponíveis:" -ForegroundColor Cyan
    $i = 1
    $options = @{}
    foreach ($k in $map.PSObject.Properties.Name) {
        Write-Host "$i. $k -> $($map.$k)"
        $options[$i] = $k
        $i++
    }
    $choice = Read-Host "Digite o número do gatilho desejado"
    if ($options.ContainsKey([int]$choice)) {
        $trigger = $options[[int]$choice]
    } else {
        Write-Host "❌ Opção inválida."
        exit
    }
}

$key = $map.PSObject.Properties.Name | Where-Object { $_ -ieq $trigger }

if ($key) {
    $file = $map.$key
    if (Test-Path $file) {
        Write-Host "🔑 Trigger '$trigger' encontrado. Abrindo: $file"
        notepad $file
        if ($trigger -ieq "Gatomia") {
            foreach ($proj in @("projects/Itau/Itau.md","projects/Renderizador/Renderizador.md","projects/Imoveis/Imoveis.md","projects/Textos/Textos.md")) {
                if (Test-Path $proj) {
                    notepad $proj
                }
            }
        }
    } else {
        Write-Host "⚠️ O arquivo '$file' não existe no disco."
    }
} else {
    Write-Host "❌ Trigger '$trigger' não encontrado no triggers.json."
}
