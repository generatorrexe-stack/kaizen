#!/bin/bash
set -e

echo "🚀 Instalando Kaizen..."

KAIZEN_DIR="$HOME/.local/share/kaizen"
BIN_DIR="$HOME/.local/bin"

# 1. Crear directorios
mkdir -p "$KAIZEN_DIR"
mkdir -p "$BIN_DIR"

# 2. Copiar el proyecto
echo "📂 Copiando archivos a $KAIZEN_DIR..."

cp -r ./. "$KAIZEN_DIR/"

# 3. Hacer ejecutables los scripts
echo "🔐 Configurando permisos..."

chmod +x "$KAIZEN_DIR/bin/kaizen"
chmod +x "$KAIZEN_DIR/bin/kaizen-sddm-deploy.sh"
chmod +x "$KAIZEN_DIR/bin/restore_state.sh"
chmod +x "$KAIZEN_DIR/bin/kaizen-privileged"
chmod +x "$KAIZEN_DIR/bin/kaizen-yay-auth"
chmod +x "$KAIZEN_DIR/hooks/apps/docker-post-install.sh"

echo "🛡️ Instalando políticas Polkit de Kaizen..."
sudo install -Dm644 "$KAIZEN_DIR/polkit/io.github.kaizen.policy" \
    /usr/share/polkit-1/actions/io.github.kaizen.policy
sudo install -Dm755 "$KAIZEN_DIR/bin/kaizen-privileged" \
    /usr/lib/kaizen/kaizen-privileged
sudo install -Dm755 "$KAIZEN_DIR/bin/kaizen-sddm-deploy.sh" \
    /usr/lib/kaizen/kaizen-sddm-deploy
sudo install -Dm755 "$KAIZEN_DIR/bin/kaizen-yay-auth" \
    /usr/lib/kaizen/kaizen-yay-auth

# 4. Crear comando global
echo "🔗 Creando comando global 'kaizen'..."

ln -sf "$KAIZEN_DIR/bin/kaizen" "$BIN_DIR/kaizen"

# 5. Instalar dependencias
echo "📦 Instalando dependencias..."

sudo pacman -S --needed \
    python \
    python-gobject \
    gtk3 \
    python-jinja \
    python-rich \
    --noconfirm

echo ""
echo "✅ ¡Kaizen instalado correctamente!"
echo ""
echo "👉 Ejecuta:"
echo ""
echo "   kaizen"
echo ""
