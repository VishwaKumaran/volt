import shutil
from pathlib import Path
from rich import print
from typer import Exit
from volt.core.template import (
    TEMPLATES_ROOT,
    inject_variables_in_file,
    format_with_black,
)


def generate_crud(app_path: Path, model_name: str) -> None:
    """Generate CRUD boilerplate for a given model."""
    model_lower = model_name.lower()

    # Simple pluralization (can be improved)
    if model_lower.endswith("y"):
        model_plural = model_lower[:-1] + "ies"
    else:
        model_plural = model_lower + "s"

    variables = {
        "MODEL_NAME": model_name.capitalize(),
        "MODEL_NAME_LOWER": model_lower,
        "MODEL_NAME_PLURAL": model_plural,
    }

    scaffold_root = TEMPLATES_ROOT / "fastapi" / "scaffold" / "app"

    # Map of template files to destination files
    files_to_generate = {
        scaffold_root
        / "models"
        / "model.py": app_path
        / "app"
        / "models"
        / f"{model_lower}.py",
        scaffold_root
        / "schemas"
        / "schema.py": app_path
        / "app"
        / "schemas"
        / f"{model_lower}.py",
        scaffold_root
        / "repositories"
        / "repository.py": app_path
        / "app"
        / "repositories"
        / f"{model_lower}.py",
        scaffold_root
        / "services"
        / "service.py": app_path
        / "app"
        / "services"
        / f"{model_lower}.py",
        scaffold_root
        / "routers"
        / "routes.py": app_path
        / "app"
        / "routers"
        / model_plural
        / "routes.py",
        scaffold_root
        / "routers"
        / "__init__.py": app_path
        / "app"
        / "routers"
        / model_plural
        / "__init__.py",
    }

    for src, dest in files_to_generate.items():
        if dest.exists():
            print(f"{dest} already exists")
            raise Exit(1)

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest)
        inject_variables_in_file(dest, variables)
        print(f"[green]✔ Created {dest.relative_to(app_path)}[/green]")

    register_router(app_path, model_name, model_plural)

    format_with_black(app_path)


def register_router(app_path: Path, model_name: str, model_plural: str) -> None:
    """Inject router registration into app/routers/main.py."""
    main_router_path = app_path / "app" / "routers" / "main.py"
    if not main_router_path.exists():
        print(
            f"[red]Error: {main_router_path} not found. Could not register router.[/red]"
        )
        return

    model_lower = model_name.lower()
    content = main_router_path.read_text()

    import_line = f"from app.routers import {model_lower}\n"
    registration_line = f'api_router.include_router({model_lower}.router, prefix="/{model_plural}", tags=["{model_plural}"])\n'

    # Add import if not present
    if import_line not in content:
        # Insert after other imports
        lines = content.splitlines()
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                last_import_idx = i
        lines.insert(last_import_idx + 1, import_line.strip())
        content = "\n".join(lines) + "\n"

    # Add registration if not present
    if registration_line not in content:
        content += registration_line

    main_router_path.write_text(content)
    print(
        f"[green]✔ Registered router in {main_router_path.relative_to(app_path)}[/green]"
    )
