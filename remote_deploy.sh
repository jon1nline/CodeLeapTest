#!/bin/bash
set -e

# --- CONFIGURAÇÃO ---
USER="ubuntu"
COMPOSE_FILE="docker-compose.yml"
APP_BASE_DIR="/home/$USER"
DEPLOY_DIR="$APP_BASE_DIR/deploy"
RELEASES_DIR="$APP_BASE_DIR/releases"
CURRENT_LINK="$APP_BASE_DIR/current"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
NEW_RELEASE_DIR="$RELEASES_DIR/$TIMESTAMP"
RELEASES_TO_KEEP=1

# --- CRIAÇÃO DA NOVA RELEASE ---
echo "INFO: Criando nova release em $NEW_RELEASE_DIR"
mkdir -p "$RELEASES_DIR" # Garante que o diretório de releases exista
# Copia todo o conteúdo (incluindo arquivos ocultos) preservando permissões
cp -a "$DEPLOY_DIR/." "$NEW_RELEASE_DIR/"

# --- CONFIGURAR .env PRIMEIRO ---
echo "INFO: Configurando .env na nova release..."
cd "$NEW_RELEASE_DIR"

# Verificar se .env.example existe antes de mover
if [ -f ".env.example" ]; then
    echo "INFO: Renomeando .env.example para .env"
    mv .env.example .env
else
    echo "ERROR: .env.example não encontrado em $NEW_RELEASE_DIR/"
    echo "Arquivos no diretório:"
    ls -la
    exit 1
fi

# --- ATIVAÇÃO DA NOVA RELEASE ---
echo "INFO: Atualizando link simbólico para a nova release..."
ln -sfn "$NEW_RELEASE_DIR" "$CURRENT_LINK"

# Navega para o diretório da release ativa (agora via link simbólico)
cd "$CURRENT_LINK"

echo "🚀 Alterar porta de comunicação da api EC2..."
# Altera o mapeamento da porta de 8000:8000 para 80:8000
sed -i 's/"8000:8000"/"80:8000"/g' "$COMPOSE_FILE"

echo "🚀 Iniciando deploy no servidor EC2..."

# --- DOCKER ---
# (Re)constrói e sobe os containers MINIMIZANDO O DOWNTIME
echo "INFO: 🐳 Subindo containers com Docker Compose..."
docker compose up -d --build --remove-orphans

# --- BANCO DE DADOS E APLICAÇÃO ---
# Aplica migrações do Django
echo "INFO: 🛠️ Aplicando migrações..."
docker compose exec api python manage.py migrate

# Carrega dados iniciais (se necessário) - **Atenção à idempotência**
echo "INFO: 📥 Carregando dados iniciais (se aplicável)..."
docker compose exec api python manage.py loaddata address
docker compose exec api python manage.py loaddata lacreiid-privacy-docs
docker compose exec api python manage.py loaddata lacreiid-intersectionality
docker compose exec api python manage.py loaddata lacreisaude

docker compose exec -T \
  -e DJANGO_SUPERUSER_EMAIL=teste@teste.com \
  -e DJANGO_SUPERUSER_PASSWORD=@teste1234 \
  api python manage.py createsuperuser --no-input || true

# --- LIMPEZA DE RELEASES ANTIGAS ---
echo "INFO: 🧹 Limpando releases antigas (mantendo as últimas $RELEASES_TO_KEEP)..."
cd "$RELEASES_DIR"
ls -1dt */ | tail -n +$(($RELEASES_TO_KEEP + 1)) | xargs -r sudo rm -rf

# --- VERIFICAÇÃO FINAL ---
echo "INFO: ✅ Containers em execução:"
cd "$CURRENT_LINK"
docker compose ps

echo "🎉 Deploy finalizado com sucesso!"