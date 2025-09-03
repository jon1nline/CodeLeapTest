FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências de build necessárias para o psycopg2 e outras ferramentas
# O '-y' permite que a instalação prossiga sem pedir confirmação.
# O 'rm -rf /var/lib/apt/lists/*' limpa o cache para reduzir o tamanho da imagem.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Copia o arquivo requirements.txt para o container
COPY requirements.txt .

# Instala as dependências do projeto Python. O '--no-cache-dir' ajuda a manter a imagem pequena.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da sua aplicação para o container
COPY . .

# Expõe a porta que a sua aplicação vai usar (ajuste se necessário)
EXPOSE 8000

# Comando para iniciar a aplicação quando o container for executado
# (Você pode ajustar este comando para o seu projeto, se for diferente)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]