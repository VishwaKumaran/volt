#!/usr/bin/env sh
set -e

BINARY_NAME="volt"
# Path to the locally built binary (adjust if your build output is different)
LOCAL_BUILD_PATH="./dist/volt"

echo "Looking for local build at: $LOCAL_BUILD_PATH"

if [ ! -f "$LOCAL_BUILD_PATH" ]; then
  echo "❌ Error: Local build not found at $LOCAL_BUILD_PATH"
  echo "Please build the project first."
  exit 1
fi

# Create local bin dir if needed
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Copy the binary
echo "Installing..."
cp "$LOCAL_BUILD_PATH" "$INSTALL_DIR/$BINARY_NAME"

chmod +x "$INSTALL_DIR/$BINARY_NAME"

echo "Installed to: $INSTALL_DIR/$BINARY_NAME"

# Add to PATH if needed
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo
  echo "⚠️  $HOME/.local/bin is not in your PATH"
  echo "Add this to your shell config:"
  echo 'export PATH="$HOME/.local/bin:$PATH"'
fi

echo
echo "✔ Local installation complete. Run: volt --help"
