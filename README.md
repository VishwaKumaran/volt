# ⚡ Volt

**Volt** is an extremely fast, modern template and stack manager for Python projects. Built for speed and simplicity, it automates the boilerplate so you can focus on building.

## Features

- **Blazing Fast**: Powered by `uv` for instant dependency resolution and environment setup.
- **Modular Stacks**: Currently supports **FastAPI** with best-practice defaults.
- **Interactive**: Beautiful CLI prompts to guide you through project creation.
- **Production Ready**: Generates structured, type-checked, and linted codebases.

## Installation

Volt requires Python 3.13+. We recommend installing it with `uv` for the best experience:

```bash
# Install via uv (Recommended)
uv tool install volt

# Or via pip
pip install volt
```

## Usage

### Create a New Project

Generate a new FastAPI application with a single command:

```bash
volt fastapi create my-app
```

Follow the interactive prompts to configure your stack (database, authentication, etc.).

### Available Stacks

- **FastAPI**: A high-performance, easy-to-learn framework for building APIs.
  - Includes options for SQLAlchemy, Pydantic, and more.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Clone the repository.
2. Install dependencies: `uv sync`
3. Run tests: `pytest`
