import shutil
from pathlib import Path

TEMPLATES_ROOT = Path(__file__).parent.parent / "templates"


def copy_template(stack: str, template_name: str, dest: Path, dirs_exist_ok: bool = False) -> None:
    src = TEMPLATES_ROOT / stack / template_name
    if not src.exists():
        raise FileNotFoundError(f"Template '{template_name}' does not exist.")
    shutil.copytree(src, dest, dirs_exist_ok=dirs_exist_ok)


def inject_variables(dest: Path, variables: dict[str, str]):
    for file in dest.rglob("*.*"):
        if file.suffix in (".py", ".toml", ".env", ".md", ".json", ".ts", ".tsx"):
            text = file.read_text()
            for key, value in variables.items():
                text = text.replace(f"__{key}__", value)
            file.write_text(text)


def inject_variables_in_file(file_path: Path, variables: dict[str, str]):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    text = file_path.read_text()

    for key, value in variables.items():
        text = text.replace(f"__{key}__", value)

    file_path.write_text(text)
