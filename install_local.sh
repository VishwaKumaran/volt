#!/usr/bin/env sh
set -e

BINARY_NAME="volt"
# Path to the locally built binary (adjust if your build output is different)
LOCAL_BUILD_PATH="./dist/volt"

echo "Looking for local build at: $LOCAL_BUILD_PATH"

if [ ! -d "$LOCAL_BUILD_PATH" ]; then
  echo "❌ Error: Local build directory not found at $LOCAL_BUILD_PATH"
  echo "Please build the project first."
  exit 1
fi

# Create local directories
INSTALL_BIN_DIR="$HOME/.local/bin"
INSTALL_LIB_DIR="$HOME/.local/lib/volt"
mkdir -p "$INSTALL_BIN_DIR"

# Clean old installation
echo "Cleaning old installation..."
rm -rf "$INSTALL_LIB_DIR"
rm -f "$INSTALL_BIN_DIR/volt"

# Copy the build directory
echo "Installing to $INSTALL_LIB_DIR..."
mkdir -p "$(dirname "$INSTALL_LIB_DIR")"
cp -r "$LOCAL_BUILD_PATH" "$INSTALL_LIB_DIR"

# Create symlink
echo "Creating symlink in $INSTALL_BIN_DIR..."
ln -s "$INSTALL_LIB_DIR/volt" "$INSTALL_BIN_DIR/volt"

chmod +x "$INSTALL_LIB_DIR/volt"

echo "Installed to: $INSTALL_BIN_DIR/volt (linked from $INSTALL_LIB_DIR)"

# Add to PATH if needed
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo
  echo "⚠️  $HOME/.local/bin is not in your PATH"
  echo "Add this to your shell config:"
  echo 'export PATH="$HOME/.local/bin:$PATH"'
fi

echo
echo "✔ Local installation complete. Run: volt --help"
