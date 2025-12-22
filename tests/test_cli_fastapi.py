from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from tests.utils.sandbox_runner import run_in_project_venv
from volt.stacks.fastapi.app_creator import create_fastapi_app

TEST_APP_DIR = Path(__file__).parent


class TestCreateFastAPIApp:
    TEST_MATRIX = [
        # Base (None, None, Docker=No, Alembic=No, Redis=No, TaskIQ=No, Sentry=No)
        ("None", "None", "No", "No", "No", "No", "No", "test_base.py"),
        # Standard SQL (SQLite, None, Docker=No, Alembic=Yes, Redis=No, TaskIQ=No, Sentry=No)
        ("SQLite", "None", "No", "Yes", "No", "No", "No", "test_db.py"),
        # Full Production Stack (PostgreSQL, Bearer Auth, Docker=Yes, Alembic=Yes, Redis=Yes, TaskIQ=Yes, Sentry=Yes)
        (
            "PostgreSQL",
            "Bearer Token (Authorization Header)",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "test_auth_bearer.py",
        ),
    ]

    @pytest.fixture
    def temp_dir(self):
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_dependencies(self):
        with patch("volt.stacks.fastapi.app_creator.choose") as mock_choose:
            yield {"choose": mock_choose}

    def _run_template_test(
        self,
        temp_dir: Path,
        mock_dependencies,
        db_choice: str,
        auth_choice: str,
        docker_choice: str,
        alembic_choice: str,
        redis_choice: str,
        taskiq_choice: str,
        sentry_choice: str,
        test_script: str,
    ):
        """Helper to create and validate generated FastAPI projects."""
        app_name = temp_dir / f"test_app"

        # Order: db, auth (if db!=None), docker, alembic (if db in SQL), redis, taskiq, sentry
        choices = [db_choice]
        if db_choice != "None":
            choices.append(auth_choice)
        choices.append(docker_choice)
        if db_choice in ["SQLite", "PostgreSQL", "MySQL"]:
            choices.append(alembic_choice)
        choices.append(redis_choice)
        choices.append(taskiq_choice)
        choices.append(sentry_choice)

        mock_dependencies["choose"].side_effect = choices

        create_fastapi_app(app_name, skip_install=False)

        # Deep assertions for production features
        if docker_choice == "Yes":
            assert (app_name / "Dockerfile").exists(), "Dockerfile missing"
            assert (
                app_name / "docker-compose.yaml"
            ).exists(), "docker-compose.yaml missing"

            compose_content = (app_name / "docker-compose.yaml").read_text()
            if db_choice not in ["None", "SQLite"]:
                assert (
                    "db:" in compose_content
                ), "DB service missing in docker-compose.yaml"
            if redis_choice == "Yes" or taskiq_choice == "Yes":
                assert (
                    "redis:" in compose_content
                ), "Redis service missing in docker-compose.yaml"
            if taskiq_choice == "Yes":
                assert (
                    "worker:" in compose_content
                ), "Worker service missing in docker-compose.yaml"

        main_py = (app_name / "app" / "main.py").read_text()
        if redis_choice == "Yes":
            assert "init_redis" in main_py, "Redis init missing in main.py"
        if taskiq_choice == "Yes":
            assert "broker.startup" in main_py, "TaskIQ startup missing in main.py"
        if sentry_choice == "Yes":
            assert "sentry_sdk.init" in main_py, "Sentry init missing in main.py"

        if alembic_choice == "Yes":
            assert (app_name / "alembic.ini").exists(), "alembic.ini missing"
            assert (app_name / "migrations").exists(), "migrations folder missing"

        return run_in_project_venv(app_name, TEST_APP_DIR / test_script)

    @pytest.mark.parametrize(
        "db_choice,auth_choice,docker_choice,alembic_choice,redis_choice,taskiq_choice,sentry_choice,test_script",
        TEST_MATRIX,
    )
    def test_generated_fastapi_templates(
        self,
        temp_dir,
        mock_dependencies,
        db_choice,
        auth_choice,
        docker_choice,
        alembic_choice,
        redis_choice,
        taskiq_choice,
        sentry_choice,
        test_script,
    ):
        """Integration tests for generated FastAPI templates."""
        self._run_template_test(
            temp_dir,
            mock_dependencies,
            db_choice,
            auth_choice,
            docker_choice,
            alembic_choice,
            redis_choice,
            taskiq_choice,
            sentry_choice,
            test_script,
        )

    #
    # # Test 13: App already exists
    # def test_create_app_already_exists(self, temp_dir, mock_dependencies, capsys):
    #     """Test that creating an app in an existing directory fails gracefully."""
    #     app_name = temp_dir / "test_app"
    #     app_name.mkdir(parents=True)
    #     mock_dependencies["choose"].side_effect = ["None", "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     captured = capsys.readouterr()
    #     assert "already exists" in captured.out
    #     mock_dependencies["install"].assert_not_called()
    #
    # # Test 14: User cancels during prompts
    # def test_create_app_user_cancels(self, temp_dir, mock_dependencies):
    #     """Test that user canceling the prompt doesn't create the app."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = KeyboardInterrupt()
    #
    #     create_fastapi_app(app_name)
    #
    #     assert not app_name.exists()
    #     mock_dependencies["install"].assert_not_called()
    #
    # # Test 15: Skip installation flag
    # def test_create_app_skip_install(self, temp_dir, mock_dependencies):
    #     """Test creating an app with skip_install=True."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = ["SQLite", "None"]
    #
    #     create_fastapi_app(app_name, skip_install=True)
    #
    #     assert app_name.exists()
    #     mock_dependencies["install"].assert_not_called()
    #
    # # Test 16: Path as string
    # def test_create_app_with_string_path(self, temp_dir, mock_dependencies):
    #     """Test creating an app with a string path."""
    #     app_name = str(temp_dir / "test_app")
    #     mock_dependencies["choose"].side_effect = ["None", "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     assert Path(app_name).exists()
    #     mock_dependencies["install"].assert_called_once()
    #
    # # Test 17: Generated configuration files
    # def test_create_app_generates_config_files(self, temp_dir, mock_dependencies):
    #     """Test that .env and .env.example files are generated."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = ["PostgreSQL", "Bearer Token (Authorization Header)"]
    #
    #     create_fastapi_app(app_name)
    #
    #     assert (app_name / ".env").exists()
    #     assert (app_name / ".env.example").exists()
    #
    #     env_content = (app_name / ".env").read_text()
    #     assert "DB_HOST" in env_content
    #     assert "SECRET_KEY" in env_content
    #
    #     env_example_content = (app_name / ".env.example").read_text()
    #     assert "DB_HOST=" in env_example_content
    #     assert "SECRET_KEY=" in env_example_content
    #
    # # Test 18: All SQL databases (SQLite, PostgreSQL, MySQL)
    # @pytest.mark.parametrize("db_choice", ["SQLite", "PostgreSQL", "MySQL"])
    # def test_create_app_all_sql_databases(self, temp_dir, mock_dependencies, db_choice):
    #     """Test creating apps with all SQL database options."""
    #     app_name = temp_dir / f"test_app_{db_choice.lower()}"
    #     mock_dependencies["choose"].side_effect = [db_choice, "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     assert app_name.exists()
    #     assert (app_name / "app" / "core" / "db.py").exists()
    #     config_content = (app_name / "app" / "core" / "config.py").read_text()
    #     assert "DATABASE_URI" in config_content
    #
    # # Test 19: All authentication methods
    # @pytest.mark.parametrize("auth_choice", [
    #     "None",
    #     "Bearer Token (Authorization Header)",
    #     "Cookie-based Authentication (HTTPOnly)"
    # ])
    # def test_create_app_all_auth_methods(self, temp_dir, mock_dependencies, auth_choice):
    #     """Test creating apps with all authentication options."""
    #     app_name = temp_dir / f"test_app_auth_{auth_choice.replace(' ', '_')}"
    #     mock_dependencies["choose"].side_effect = ["None", auth_choice]
    #
    #     create_fastapi_app(app_name)
    #
    #     assert app_name.exists()
    #     if auth_choice != "None":
    #         assert (app_name / "app" / "routers" / "auth" / "router.py").exists()
    #         assert (app_name / "app" / "core" / "security.py").exists()
    #         config_content = (app_name / "app" / "core" / "config.py").read_text()
    #         assert "SECRET_KEY" in config_content
    #
    # # Test 20: Error handling during creation
    # def test_create_app_error_during_creation(self, temp_dir, mock_dependencies, capsys):
    #     """Test that errors during creation are handled properly."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = ["None", "None"]
    #
    #     with patch("volt.stacks.fastapi.app_creator.copy_fastapi_base_template") as mock_copy:
    #         mock_copy.side_effect = Exception("Template copy failed")
    #
    #         create_fastapi_app(app_name)
    #
    #         captured = capsys.readouterr()
    #         assert "Error creating FastAPI app" in captured.out
    #
    # # Test 21: Project name injection in config
    # def test_create_app_project_name_injection(self, temp_dir, mock_dependencies):
    #     """Test that project name is correctly injected in config."""
    #     app_name = temp_dir / "my_awesome_app"
    #     mock_dependencies["choose"].side_effect = ["None", "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     config_content = (app_name / "app" / "core" / "config.py").read_text()
    #     assert "my_awesome_app" in config_content
    #
    # # Test 22: Healthcheck route injection for SQL databases
    # @pytest.mark.parametrize("db_choice", ["SQLite", "PostgreSQL", "MySQL"])
    # def test_create_app_healthcheck_sql(self, temp_dir, mock_dependencies, db_choice):
    #     """Test that healthcheck route is added for SQL databases."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = [db_choice, "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     main_content = (app_name / "app" / "main.py").read_text()
    #     assert "/health" in main_content
    #     assert "get_session" in main_content
    #
    # # Test 23: Healthcheck route injection for MongoDB
    # def test_create_app_healthcheck_mongodb(self, temp_dir, mock_dependencies):
    #     """Test that healthcheck route is added for MongoDB."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = ["MongoDB", "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     main_content = (app_name / "app" / "main.py").read_text()
    #     assert "/health" in main_content
    #     assert "client.admin.command" in main_content
    #
    # # Test 24: User model injection for SQL databases
    # @pytest.mark.parametrize("db_choice", ["SQLite", "PostgreSQL", "MySQL"])
    # def test_create_app_user_model_sql(self, temp_dir, mock_dependencies, db_choice):
    #     """Test that User model is properly created for SQL databases with auth."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = [db_choice, "Bearer Token (Authorization Header)"]
    #
    #     create_fastapi_app(app_name)
    #
    #     user_model = (app_name / "app" / "models" / "user.py").read_text()
    #     assert "class User(Base)" in user_model
    #     assert "__tablename__" in user_model
    #     assert "username" in user_model
    #
    # # Test 25: User model injection for MongoDB
    # def test_create_app_user_model_mongodb(self, temp_dir, mock_dependencies):
    #     """Test that User model is properly created for MongoDB with auth."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = ["MongoDB", "Bearer Token (Authorization Header)"]
    #
    #     create_fastapi_app(app_name)
    #
    #     user_model = (app_name / "app" / "models" / "user.py").read_text()
    #     assert "class User(Document)" in user_model
    #     assert "Settings" in user_model
    #     assert "users" in user_model
    #
    # # Test 26: Lifespan injection for MongoDB
    # def test_create_app_mongodb_lifespan(self, temp_dir, mock_dependencies):
    #     """Test that lifespan context manager is added for MongoDB."""
    #     app_name = temp_dir / "test_app"
    #     mock_dependencies["choose"].side_effect = ["MongoDB", "None"]
    #
    #     create_fastapi_app(app_name)
    #
    #     main_content = (app_name / "app" / "main.py").read_text()
    #     assert "lifespan" in main_content
    #     assert "init_db" in main_content
    #     assert "close_db" in main_content
    #
    # # Test 27: Complete matrix test (all combinations)
    # @pytest.mark.parametrize("db_choice,auth_choice", [
    #     ("None", "None"),
    #     ("None", "Bearer Token (Authorization Header)"),
    #     ("None", "Cookie-based Authentication (HTTPOnly)"),
    #     ("SQLite", "None"),
    #     ("SQLite", "Bearer Token (Authorization Header)"),
    #     ("SQLite", "Cookie-based Authentication (HTTPOnly)"),
    #     ("PostgreSQL", "None"),
    #     ("PostgreSQL", "Bearer Token (Authorization Header)"),
    #     ("PostgreSQL", "Cookie-based Authentication (HTTPOnly)"),
    #     ("MySQL", "None"),
    #     ("MySQL", "Bearer Token (Authorization Header)"),
    #     ("MySQL", "Cookie-based Authentication (HTTPOnly)"),
    #     ("MongoDB", "None"),
    #     ("MongoDB", "Bearer Token (Authorization Header)"),
    #     ("MongoDB", "Cookie-based Authentication (HTTPOnly)"),
    # ])
    # def test_create_app_all_combinations(self, temp_dir, mock_dependencies, db_choice, auth_choice):
    #     """Test all possible combinations of database and authentication."""
    #     app_name = temp_dir / f"test_app_{db_choice}_{auth_choice.replace(' ', '_')}"
    #     mock_dependencies["choose"].side_effect = [db_choice, auth_choice]
    #
    #     create_fastapi_app(app_name)
    #
    #     assert app_name.exists()
    #     assert (app_name / "app" / "main.py").exists()
    #     assert (app_name / "app" / "core" / "config.py").exists()
    #
    #     # Verify database setup
    #     if db_choice != "None":
    #         assert (app_name / "app" / "core" / "db.py").exists()
    #
    #     # Verify authentication setup
    #     if auth_choice != "None":
    #         assert (app_name / "app" / "routers" / "auth" / "router.py").exists()
    #         assert (app_name / "app" / "core" / "security.py").exists()
