#!/bin/bash
set -e

# --- CONFIGURAÇÃO ---
# Usuário no servidor remoto
USER="ubuntu"
# Nome do arquivo docker-compose
COMPOSE_FILE="docker-compose.yml"
# Diretório base da aplicação no servidor
APP_BASE_DIR="/home/$USER"
# Diretório onde o código é copiado para deploy
DEPLOY_DIR="$APP_BASE_DIR/deploy"
# Diretório onde as releases serão armazenadas
RELEASES_DIR="$APP_BASE_DIR/releases"
# Link simbólico para a release ativa
CURRENT_LINK="$APP_BASE_DIR/current"
# Timestamp para nomear a nova release
TIMESTAMP=$(date +%Y%m%d%H%M%S)
# Diretório da nova release
NEW_RELEASE_DIR="$RELEASES_DIR/$TIMESTAMP"
# Número de releases antigas para manter
RELEASES_TO_KEEP=1

# --- CRIAÇÃO DA NOVA RELEASE ---
echo "INFO: Criando nova release em $NEW_RELEASE_DIR"
mkdir -p "$RELEASES_DIR" # Garante que o diretório de releases exista
# Copia todo o conteúdo (incluindo arquivos ocultos) preservando permissões
cp -a "$DEPLOY_DIR/." "$NEW_RELEASE_DIR/"

# --- ATIVAÇÃO DA NOVA RELEASE ---
echo "INFO: Atualizando link simbólico para a nova release..."
ln -sfn "$NEW_RELEASE_DIR" "$CURRENT_LINK"

# Navega para o diretório da release ativa
cd "$CURRENT_LINK"
echo "INFO: Configurando .env na nova release..."
# Renomeia o arquivo .env.example para .env
mv .env.example .env

echo "INFO: Alterando porta de comunicação da API para 80:8000..."
# Altera o mapeamento da porta de 8000:8000 para 80:8000
sed -i 's/"8000:8000"/"80:8000"/g' "$COMPOSE_FILE"

echo "INFO: 🚀 Iniciando deploy no servidor EC2..."

# --- DOCKER ---
# (Re)constrói e sobe os containers MINIMIZANDO O DOWNTIME
echo "INFO: 🐳 Subindo containers com Docker Compose..."
docker-compose up -d --build --remove-orphans

# --- BANCO DE DADOS E APLICAÇÃO ---
# Aplica migrações do Django
echo "INFO: 🛠️ Aplicando migrações..."
docker-compose exec api python manage.py migrate

# Carrega dados iniciais (se necessário) - **Atenção à idempotência**
echo "INFO: 📥 Carregando dados iniciais (se aplicável)..."
# '|| true' permite que o script continue se o comando de carga de dados falhar
docker-compose exec api python manage.py loaddata address || true
docker-compose exec api python manage.py loaddata lacreiid-privacy-docs || true
docker-compose exec api python manage.py loaddata lacreiid-intersectionality || true
docker-compose exec api python manage.py loaddata lacreisaude || true

echo "INFO: Criando superusuário..."
# '|| true' permite que o script continue se o superusuário já existir
docker-compose exec -T \
  -e DJANGO_SUPERUSER_EMAIL=teste@teste.com \
  -e DJANGO_SUPERUSER_PASSWORD=@teste1234 \
  api python manage.py createsuperuser --no-input || true

# --- LIMPEZA DE RELEASES ANTIGAS ---
echo "INFO: 🧹 Limpando releases antigas (mantendo as últimas $RELEASES_TO_KEEP)..."
cd "$RELEASES_DIR"
# O 'ls -1t' lista os diretórios por tempo, o 'tail' pega os mais antigos e o 'xargs' os apaga
ls -1t */ | tail -n +$(($RELEASES_TO_KEEP + 1)) | xargs -r sudo rm -rf

# --- VERIFICAÇÃO FINAL ---
echo "INFO: ✅ Containers em execução:"
cd "$CURRENT_LINK"
docker-compose ps

echo "SUCCESS: 🎉 Deploy finalizado com sucesso!"