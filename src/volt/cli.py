import argparse

from volt.core.project import create_project


def main():
    parser = argparse.ArgumentParser(prog="volt", description="Volt ⚡ - Multi-stack project generator")

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_fastapi = subparsers.add_parser(
        "create-fastapi-app",
        help="Create a minimal FastAPI project"
    )
    parser_fastapi.add_argument("name", help="Name of the project to create")
    parser_fastapi.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip dependency installation"
    )

    args = parser.parse_args()

    if args.command == "create-fastapi-app":
        create_project(args.name, "fastapi", skip_install=args.skip_install)
