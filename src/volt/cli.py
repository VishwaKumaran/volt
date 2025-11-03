from typer import Typer

from volt.stacks.fastapi.cli import fastapi_app

app = Typer(
    help="An extremely fast template and stack manager for Python projects.",
    no_args_is_help=True,
)

app.add_typer(fastapi_app, name="fastapi", no_args_is_help=True)


def main():
    app()


if __name__ == "__main__":
    main()
