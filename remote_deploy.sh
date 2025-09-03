#!/bin/bash
set -e

# --- CONFIGURAÇÃO ---
# Usuário no servidor remoto
USER="ubuntu"
# Diretório onde o novo código será copiado
APP_DIR="/home/$USER/deploy"
# Diretório para onde o deploy anterior será movido


echo "INFO: Renomeando .env.example para .env"
mv "$APP_DIR/.env.example" "$APP_DIR/.env"

echo "INFO: Alterando mapeamento de portas no docker-compose.yml"
# Exemplo de alteração de porta, ajuste conforme a sua necessidade
sed -i 's/"8000:8000"/"80:8000"/g' "$APP_DIR/docker-compose.yml"

# --- DOCKER ---
echo "INFO: 🐳 Parando e removendo containers antigos (se existirem)..."
# O comando 'down' remove os containers e volumes associados
docker-compose -f "docker-compose.yml" down --volumes --remove-orphans || true

echo "INFO: 🐳 Subindo containers com Docker Compose..."
# (Re)constrói e sobe os containers. Usamos o nome do diretório como prefixo do projeto.
docker-compose -f "docker-compose.yml" up -d --build

# --- BANCO DE DADOS E APLICAÇÃO ---
echo "INFO: 🛠️ Aplicando migrações..."
# Removi o '|| true' para que o erro seja exibido se a migração falhar.
# Altere 'web' para o nome do seu serviço se for diferente.
docker-compose -f "docker-compose.yml" exec deploy_web python manage.py migrate

# --- VERIFICAÇÃO FINAL ---
echo "INFO: Containers em execução:"
docker-compose ps

echo "SUCCESS: 🎉 Deploy finalizado com sucesso!"