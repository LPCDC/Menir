# Usar Python leve
FROM python:3.11-slim

# Configurar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (se precisar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto
COPY . .

# Definir variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1

# Comando padrão (será sobrescrito pelo docker-compose, mas bom ter)
CMD ["python", "-m", "menir10.service_watcher"]
