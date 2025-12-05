# ==========================================================
# Script de setup inicial dos projetos Training U (PowerShell)
# Agora com Gatomia como função global
# ==========================================================

$base = "projects"

# Criar pastas
$dirs = @(
  "$base\Gatomia",
  "$base\Itau\Propostas",
  "$base\Itau\Processos",
  "$base\Renderizador\Tania\Familia_Otani",
  "$base\Imoveis\Santos",
  "$base\Imoveis\SaoPaulo",
  "$base\Textos\Subprojeto1",
  "$base\Textos\Subprojeto2",
  "$base\TrainingU"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ }

# Criar Gatomia.md
@"
# Função Gatomia

## Contexto  
Gatomia é a função central do Menir que agrega todos os projetos existentes em uma visão consolidada.

## Projetos
- [Itaú](../Itau/Itau.md)  
- [Renderizador](../Renderizador/Renderizador.md)  
- [Imóveis](../Imoveis/Imoveis.md)  
- [Textos](../Textos/Textos.md)  

## Status  
CENTRAL  
"@ | Set-Content "$base\Gatomia\Gatomia.md" -Encoding UTF8

# Aqui manter todos os outros arquivos antigos já feitos: Itau.md, Proposta, Renderizador, etc.

# Atualizar triggers.json
@"
{
  "Gatomia": "projects/Gatomia/Gatomia.md",
  "RenderStart": "projects/Renderizador/Renderizador.md",
  "Imoveis": "projects/Imoveis/Imoveis.md",
  "Textos": "projects/Textos/Textos.md"
}
"@ | Set-Content triggers.json -Encoding UTF8

Write-Host "=========================================================="
Write-Host "Setup com Gatomia criado! Estrutura + função global pronta."
Write-Host "=========================================================="
