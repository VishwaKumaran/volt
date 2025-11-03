import subprocess
from pathlib import Path

from rich import print


def run_uv(args: list[str], cwd: Path, check: bool = True):
    cmd = ["uv", *args]
    print(f"[dim]$ {' '.join(cmd)}[/dim]")
    subprocess.run(cmd, cwd=cwd, check=check)


def install_uv_packages(packages: list[str], dest: Path):
    if not packages:
        return

    print(f"[yellow]→ Installing: {', '.join(packages)}[/yellow]")
    run_uv(["add", *packages], dest)


def init_uv_project(dest: Path):
    print("[cyan]Initializing uv project...[/cyan]")
    run_uv(["init"], dest)
    (dest / "main.py").unlink(missing_ok=True)
