# Menir – BootLocal Edition  
Repositório: LPCDC/Menir · Branch: release/menir-aio-v5.0-boot-local

## Visão Geral  
Este branch destina-se a execução local “boot” da automação AIO do Projeto Menir.  
Foca em pré-flight, configuração de ambiente e preparação de pipelines residenciais.

## Instalação  
### Pré-requisitos  
- Python 3.12  
- Conda (ou similar)  
- Driver Python para Neo4j  
- Git  
- Windows (preferencial) para execução do script PowerShell

### Passos  
```bash
git clone <repo-url>
cd Menir
git checkout release/menir-aio-v5.0-boot-local
conda activate menir
pip install -r requirements.txt