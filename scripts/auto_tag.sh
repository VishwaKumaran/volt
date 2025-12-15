#!/usr/bin/env sh
set -e

# Only run on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Info: Not on main branch ($CURRENT_BRANCH). Skipping tag check."
    exit 0
fi

# Get the version from the project using uv/python
# We use the installed package version
VERSION=$(uv run python -c "from importlib.metadata import version; print(version('volt-cli'))" 2>/dev/null)

if [ -z "$VERSION" ]; then
    echo "Error: Could not determine version from volt-cli."
    exit 1
fi

TAG_NAME="v$VERSION"

# Check if tag exists (local or remote)
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    echo "Info: Tag $TAG_NAME already exists. Skipping."
    exit 0
fi

if git ls-remote --exit-code --tags origin "$TAG_NAME" >/dev/null 2>&1; then
    echo "Info: Tag $TAG_NAME already exists on remote. Skipping."
    exit 0
fi

echo "Creating and pushing tag: $TAG_NAME"
git tag -a "$TAG_NAME" -m "Release $TAG_NAME"
git push origin "$TAG_NAME"