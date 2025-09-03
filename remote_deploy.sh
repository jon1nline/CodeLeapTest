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
mkdir -p "$RELEASES_DIR"
# Copia todo o conteúdo do diretório de deploy para a nova release
cp -a "$DEPLOY_DIR/." "$NEW_RELEASE_DIR/"

# --- CONFIGURAR .env PRIMEIRO ---
echo "INFO: Configurando .env na nova release..."
cd "$NEW_RELEASE_DIR"

if [ -f ".env.example" ]; then
    echo "INFO: Renomeando .env.example para .env"
    mv .env.example .env
else
    echo "ERROR: .env.example não encontrado em $NEW_RELEASE_DIR/"
    ls -la
    exit 1
fi

# --- ALTERAR PORTA NO DOCKER-COMPOSE ---
echo "INFO: Alterando porta de comunicação da API para 80:8000..."
# Usar caminho absoluto para o docker-compose.yml NA NOVA RELEASE
# Nota: Este comando 'sed' assume um formato específico. Pode ser frágil se o arquivo mudar.
if [ -f "$NEW_RELEASE_DIR/$COMPOSE_FILE" ]; then
    sed -i 's/8000:8000/80:8000/g' "$NEW_RELEASE_DIR/$COMPOSE_FILE"
    echo "SUCCESS: Porta alterada com sucesso."
else
    echo "ERROR: $COMPOSE_FILE não encontrado em $NEW_RELEASE_DIR/"
    echo "Arquivos no diretório:"
    ls -la "$NEW_RELEASE_DIR/"
    exit 1
fi

# --- ATIVAÇÃO DA NOVA RELEASE ---
echo "INFO: Atualizando link simbólico para a nova release..."
# O comando ln -sfn força a criação do link, removendo o antigo se existir
ln -sfn "$NEW_RELEASE_DIR" "$CURRENT_LINK"

# Navega para o diretório da release ativa
cd "$CURRENT_LINK"

echo "INFO: 🚀 Iniciando deploy no servidor EC2..."

# --- DOCKER ---
echo "INFO: 🐳 Subindo containers com Docker Compose..."
# Adicionando o flag -f para especificar explicitamente o arquivo
# de configuração. Isso resolve o problema de "file not found".
if [ -f "$CURRENT_LINK/$COMPOSE_FILE" ]; then
    docker-compose -f "$CURRENT_LINK/$COMPOSE_FILE" up -d --build --remove-orphans
else
    echo "ERROR: $COMPOSE_FILE não encontrado em $CURRENT_LINK/"
    echo "Arquivos no diretório:"
    ls -la "$CURRENT_LINK/"
    exit 1
fi

# --- BANCO DE DADOS E APLICAÇÃO ---
echo "INFO: 🛠️ Aplicando migrações..."
docker-compose exec api python manage.py migrate

echo "INFO: 📥 Carregando dados iniciais (se aplicável)..."
# O '|| true' garante que o script continue mesmo se o comando falhar
docker-compose exec api python manage.py loaddata address || true
docker-compose exec api python manage.py loaddata lacreiid-privacy-docs || true
docker-compose exec api python manage.py loaddata lacreiid-intersectionality || true
docker-compose exec api python manage.py loaddata lacreisaude || true

echo "INFO: Criando superusuário..."
docker-compose exec -T \
  -e DJANGO_SUPERUSER_EMAIL=teste@teste.com \
  -e DJANGO_SUPERUSER_PASSWORD=@teste1234 \
  api python manage.py createsuperuser --no-input || true

# --- LIMPEZA DE RELEASES ANTIGAS ---
echo "INFO: 🧹 Limpando releases antigas (mantendo as últimas $RELEASES_TO_KEEP)..."
cd "$RELEASES_DIR"
# O 'ls -1t' lista os diretórios por tempo, o 'tail' pega os mais antigos e o 'xargs' os apaga
ls -1t */ | tail -n +$(($RELEASES_TO_KEEP + 1)) | xargs -r rm -rf

# --- VERIFICAÇÃO FINAL ---
echo "SUCCESS: ✅ Containers em execução:"
cd "$CURRENT_LINK"
docker-compose ps

echo "SUCCESS: 🎉 Deploy finalizado com sucesso!"