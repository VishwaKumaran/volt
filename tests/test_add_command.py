import shutil
from pathlib import Path
from typer.testing import CliRunner
from volt.cli import app
import os
from unittest.mock import patch

runner = CliRunner()

def test_add_command_flow():
    # Create a temporary directory for the test
    with runner.isolated_filesystem():
        # Mock the 'choose' function to return desired values
        with patch("volt.stacks.fastapi.app_creator.choose") as mock_choose_create, \
             patch("volt.stacks.fastapi.adder.choose") as mock_choose_add, \
             patch("volt.stacks.fastapi.adder.install_fastapi_dependencies") as mock_install_deps, \
             patch("volt.stacks.fastapi.app_creator.install_fastapi_dependencies") as mock_install_deps_create:
            
            # Setup return values for 'create' command
            # 1. DB Choice: None
            mock_choose_create.side_effect = ["None"] 
            
            # 1. Create a fresh FastAPI project (no DB, no Auth)
            result = runner.invoke(app, ["fastapi", "create", "test-project"])
            assert result.exit_code == 0
            assert "Successfully created FastAPI app" in result.stdout
            
            project_dir = Path("test-project")
            os.chdir(project_dir)
            
            # Verify volt.toml created
            assert Path("volt.toml").exists()
            config_text = Path("volt.toml").read_text()
            assert 'stack = "fastapi"' in config_text
            
            # Create dummy pyproject.toml since we mocked dependency installation
            Path("pyproject.toml").write_text('[project]\ndependencies = ["fastapi", "sqlmodel"]\n')
            
            # Setup return values for 'add db' command
            # 1. DB Choice: SQLite
            mock_choose_add.side_effect = ["SQLite"]
            
            # 2. Add Database (SQLite)
            result = runner.invoke(app, ["add", "db"])
            assert result.exit_code == 0
            assert "Successfully added SQLite database support" in result.stdout
            
            # Verify DB files exist
            assert Path("app/core/db.py").exists()
            assert "lifespan" in Path("app/main.py").read_text()
            
            # Verify volt.toml updated with database
            config_text = Path("volt.toml").read_text()
            assert 'database = "SQLite"' in config_text
            
            # Setup return values for 'add auth' command
            # 1. Auth Choice: Bearer Token
            mock_choose_add.side_effect = ["Bearer Token (Authorization Header)"]
            
            # 3. Add Auth (Bearer)
            result = runner.invoke(app, ["add", "auth"])
            assert result.exit_code == 0
            assert "Successfully added Bearer Token" in result.stdout
            
            # Verify Auth files exist
            assert Path("app/routers/main.py").exists()
            assert "auth_router" in Path("app/routers/main.py").read_text()

            # Verify volt.toml updated with auth
            config_text = Path("volt.toml").read_text()
            assert 'auth = "Bearer Token (Authorization Header)"' in config_text
