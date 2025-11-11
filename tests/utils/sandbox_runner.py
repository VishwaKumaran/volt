import os
import subprocess
from pathlib import Path

TEST_DEPENDENCIES = ["httpx"]


def run_in_project_venv(project_path: Path, script: Path):
    venv_python = project_path / ".venv" / "bin" / "python"
    if not venv_python.exists():
        raise RuntimeError("Virtual environment not found in generated project.")

    add_proc = subprocess.run(
        ["uv", "add", ", ".join(TEST_DEPENDENCIES)],
        cwd=project_path,
        check=True,
        capture_output=True,
        text=True,
    )
    if add_proc.returncode != 0:
        raise RuntimeError(f"Failed to install {', '.join(TEST_DEPENDENCIES)} dependencies in project venv")

    result = subprocess.run(
        [str(venv_python), str(script.resolve())],
        cwd=project_path,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(project_path)},
    )

    if result.returncode != 0:
        err_msg = f"""
        [ERROR] Test script failed in project: {project_path.name}

        --- STDERR ---
        {result.stderr.strip() or '[empty]'}

        --- STDOUT ---
        {result.stdout.strip() or '[empty]'}
        """
        raise RuntimeError(err_msg.strip())

    return result
