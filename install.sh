#!/bin/bash
set -e

echo "🚀 Instalando Kaizen..."

# 1. Crear directorios necesarios
mkdir -p ~/.local/share/kaizen
mkdir -p ~/.local/bin

# 2. Copiar los archivos del repo a la carpeta de usuario
echo "📂 Copiando archivos a ~/.local/share/kaizen..."
cp -r ./* ~/.local/share/kaizen/

# 3. Hacer ejecutable el CLI
chmod +x ~/.local/share/kaizen/cli/kaizen.py

# 4. Crear un enlace simbólico (symlink) para usar 'kaizen' desde cualquier lado
echo "🔗 Creando comando global 'kaizen'..."
ln -sf ~/.local/share/kaizen/cli/kaizen.py ~/.local/bin/kaizen

# 5. Instalar dependencias de Python (Asegúrate de tener yay o pacman listo)
echo "📦 Instalando dependencias necesarias..."
sudo pacman -S --needed python-gobject gtk3 python-jinja python-rich --noconfirm

echo ""
echo "✅ ¡Instalación completa!"
echo "👉 Escribe 'kaizen gui' o 'kaizen help' para empezar."
