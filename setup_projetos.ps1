# ==========================================================
# Script de setup inicial dos projetos Training U (PowerShell)
# Cria pastas, arquivos e popula com conteúdo padrão
# ==========================================================

$base = "projects"

# Criar pastas
$dirs = @(
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

# Criar index.md
@"
# Training U — Menu Geral

## Núcleo
- [Training U — GPT-5 Controls](projects/TrainingU/Training_U_gpt5_controls.md)

## Projetos
- [Itaú](projects/Itau/Itau.md)
  - [Proposta 15220012](projects/Itau/Propostas/Proposta_15220012.md)
  - [Jurídico](projects/Itau/Processos/Juridico.md)
  - [Extratos](projects/Itau/Processos/Extratos_Indexados.md)

- [Renderizador](projects/Renderizador/Renderizador.md)
  - [Tânia](projects/Renderizador/Tania/Tania.md)
    - [Família Otani](projects/Renderizador/Tania/Familia_Otani/Familia_Otani.md)

- [Imóveis](projects/Imoveis/Imoveis.md)
  - [Santos](projects/Imoveis/Santos/Santos.md)
  - [São Paulo](projects/Imoveis/SaoPaulo/SaoPaulo.md)
    - [Guarani 151 Locação](projects/Imoveis/SaoPaulo/Guarani151_Locacao.md)

- [Textos](projects/Textos/Textos.md)
  - [Subprojeto 1](projects/Textos/Subprojeto1/Subprojeto1.md)
  - [Subprojeto 2](projects/Textos/Subprojeto2/Subprojeto2.md)

---

📌 **Regras:**
- SEMPRE criar um .md por projeto/subprojeto.
- ATUALIZAR este index.md quando abrir algo novo.
- STATUS deve aparecer no cabeçalho de cada .md.
"@ | Set-Content index.md -Encoding UTF8

# Criar triggers.json
@"
{
  "Gatomia": "projects/Itau/Itau.md",
  "RenderStart": "projects/Renderizador/Renderizador.md",
  "Imoveis": "projects/Imoveis/Imoveis.md",
  "Textos": "projects/Textos/Textos.md"
}
"@ | Set-Content triggers.json -Encoding UTF8

# Criar Itau.md
@"
# Projeto Itaú

## Contexto
Dossiê completo do relacionamento com o Banco Itaú, incluindo propostas, processos jurídicos e extratos.  
Subprojeto principal: **Proposta 15220012**.

## Status
ATIVO

## Linha do Tempo
- [2025-09-14] Registro inicial no Training U
- [2025-09-19] Integração gatilho "Gatomia"

## Checklist
- [ ] Organizar documentos da Proposta 15220012
- [ ] Indexar extratos bancários
- [ ] Consolidar histórico de atendimento (Renata, Tatiana, Júlio)

## Artefatos Relacionados
- itau_ingest.cypher
- itau_queries.cypher
- itaui.js
"@ | Set-Content "$base\Itau\Itau.md" -Encoding UTF8

# Criar Proposta_15220012.md
@"
# Proposta 15220012

## Contexto
Proposta formalizada com garantia de imóvel.

## Status
EM CURSO

## Linha do Tempo
- [2025-09-15] E-mail de Júlio recebido
- [2025-09-18] Evento corporativo do Itaú detectado

## Checklist
- [ ] Consolidar anexos
- [ ] Indexar histórico de atendimento
- [ ] Preparar defesa documental
"@ | Set-Content "$base\Itau\Propostas\Proposta_15220012.md" -Encoding UTF8

# Criar Renderizador.md
@"
# Projeto Renderizador

## Contexto
Camada de renderização arquitetônica via IA.  
Cliente principal: **Tânia** → subcliente Família Otani.

## Status
ATIVO

## Linha do Tempo
- [2025-09-13] Cena 001 (Família Otani) recebida
- [2025-09-19] Estrutura hierárquica definida no Training U

## Checklist
- [ ] Consolidar prompts MyArchitectAI em inglês
- [ ] Indexar cenas no formato Otani_[Ambiente]_[Ângulo]_S[1-6]_YYYY-MM-DD_vN.png
- [ ] Gerar booklet para Família Otani

## Artefatos Relacionados
- Screenshots do SketchUp
- Prompts MyArchitectAI
"@ | Set-Content "$base\Renderizador\Renderizador.md" -Encoding UTF8

# Criar Familia_Otani.md
@"
# Família Otani

## Contexto
Cliente da arquiteta Tânia, foco no altar budista e cenas do projeto residencial.

## Status
ATIVO

## Linha do Tempo
- [2025-09-13] Cena 001 registrada
- [2025-09-19] Definição do moodboard inicial

## Checklist
- [ ] Renderizar cenas adicionais
- [ ] Consolidar moodboard
- [ ] Entregar booklet para apresentação
"@ | Set-Content "$base\Renderizador\Tania\Familia_Otani\Familia_Otani.md" -Encoding UTF8

# Criar Imoveis.md
@"
# Projeto Imóveis

## Contexto
Gestão de ativos imobiliários em Santos e São Paulo.

## Status
ATIVO

## Linha do Tempo
- [2025-09-19] Estrutura inicial definida no Training U

## Checklist
- [ ] Consolidar docs de Santos
- [ ] Consolidar docs de São Paulo
"@ | Set-Content "$base\Imoveis\Imoveis.md" -Encoding UTF8

# Criar Guarani151_Locacao.md
@"
# Guarani 151 Locação

## Contexto
Histórico de locação do imóvel Guarani 151 em São Paulo.

## Status
ARQUIVADO

## Linha do Tempo
- [2018] Contrato de locação
- [2025-09-14] Indexado no Training U
"@ | Set-Content "$base\Imoveis\SaoPaulo\Guarani151_Locacao.md" -Encoding UTF8

# Criar Textos.md
@"
# Projeto Textos

## Contexto
Repositório de ideias e subprojetos de texto.

## Status
EM CURSO

## Linha do Tempo
- [2025-09-19] Estrutura inicial definida no Training U

## Checklist
- [ ] Definir subprojetos ativos
- [ ] Consolidar drafts em .md

## Subprojetos
- Subprojeto 1: ideias iniciais
- Subprojeto 2: rascunhos avançados
"@ | Set-Content "$base\Textos\Textos.md" -Encoding UTF8

Write-Host "=========================================================="
Write-Host "Setup concluído! Arquivos e pastas criados com sucesso."
Write-Host "=========================================================="
