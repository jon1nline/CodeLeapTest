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

# --- DOCKERIZAÇÃO ---
echo "INFO: Iniciando os containers Docker..."
cd "$APP_DIR"
docker-compose up -d --build --remove-orphans

# --- VERIFICAÇÃO FINAL ---
echo "INFO: Containers em execução:"
docker-compose ps

echo "SUCCESS: 🎉 Deploy finalizado com sucesso!