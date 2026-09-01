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

