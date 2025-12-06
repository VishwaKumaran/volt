#!/usr/bin/env sh
set -e

REPO="VishwaKumaran/volt"
BINARY_NAME="volt"

# Detect OS
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
  linux)
    case "$ARCH" in
      x86_64) FILE="volt-linux-x86_64" ;;
      aarch64|arm64) FILE="volt-linux-arm64" ;;
      *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
    esac
    ;;
  darwin)
    case "$ARCH" in
      x86_64) FILE="volt-macos-x86_64" ;;
      arm64)  FILE="volt-macos-arm64" ;;
      *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
    esac
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac

# Fetch latest release tag
TAG=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" \
  | grep '"tag_name"' \
  | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$TAG" ]; then
  echo "❌ Error: Unable to find latest release tag."
  echo "Typically this happens if no releases have been published yet."
  exit 1
fi

URL="https://github.com/$REPO/releases/download/$TAG/$FILE"

echo "Downloading: $URL"

# Create local bin dir if needed
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Download
if ! curl -L --fail "$URL" -o "$INSTALL_DIR/$BINARY_NAME"; then
  echo "❌ Error: Download failed."
  exit 1
fi

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
echo "✔ Installation complete. Run: volt --help"