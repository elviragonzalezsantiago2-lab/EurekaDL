#!/usr/bin/env bash
# Install script for EurekaDL CLI alias 'eureka'
# Supports Termux, Linux, macOS, and iOS (a-Shell/iSH) environments.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install_eureka.sh [--prefix /target/bin]

Creates a small wrapper named 'eureka' in a user-writable bin directory so
you can run the CLI as: eureka [args...]

By default it installs to:
 - Termux: $PREFIX/bin
 - macOS (Homebrew): $(brew --prefix)/bin (if available) or /usr/local/bin
 - Linux: $HOME/.local/bin
 - iOS (a-Shell/iSH): $HOME/bin

Pass --prefix to override the target bin directory.
EOF
}

PREFIX_ARG=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --prefix) PREFIX_ARG="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

# Resolve repo root (assumes script is located in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Detect platform and choose default bin dir
if [ -n "${PREFIX_ARG}" ]; then
  TARGET_DIR="$PREFIX_ARG"
else
  if [ -n "${TERMUX_VERSION:-}" ]; then
    TARGET_DIR="${PREFIX:-/data/data/com.termux/files/usr}/bin"
  else
    UNAME="$(uname -s)"
    if [ "$UNAME" = "Darwin" ]; then
      # macOS: prefer brew prefix if available
      if command -v brew >/dev/null 2>&1; then
        BREW_PREFIX="$(brew --prefix)"
        TARGET_DIR="$BREW_PREFIX/bin"
      else
        TARGET_DIR="/usr/local/bin"
      fi
    else
      # Default Linux / iOS shells (a-Shell, iSH) fallback
      # Prefer $HOME/.local/bin, then $HOME/bin
      if [ -d "$HOME/.local/bin" ] || [ -w "$HOME" ]; then
        TARGET_DIR="$HOME/.local/bin"
      else
        TARGET_DIR="$HOME/bin"
      fi
    fi
  fi
fi

mkdir -p "$TARGET_DIR"

WRAPPER_PATH="$TARGET_DIR/eureka"

# Create wrapper script that calls the repository's eureka.py
cat > "$WRAPPER_PATH" <<EOF
#!/usr/bin/env bash
# Wrapper to run EurekaDL from installed repository
exec python3 "${REPO_ROOT}/eureka.py" "\$@"
EOF

chmod +x "$WRAPPER_PATH"

# If directory not in PATH, print helpful message
case ":$PATH:" in
  *":$TARGET_DIR:"*)
    echo "Installed 'eureka' to $WRAPPER_PATH"
    ;;
  *)
    echo "Installed 'eureka' to $WRAPPER_PATH"
    echo "Note: $TARGET_DIR is not in your PATH. Add it to run 'eureka' directly."
    echo "  e.g. export PATH=\"$TARGET_DIR:\$PATH\"  # add to ~/.profile or ~/.bashrc"
    ;;
esac

echo "Run 'eureka --help' to verify."
