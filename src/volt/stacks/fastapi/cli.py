from typer import Typer

fastapi_app = Typer(help="Create, configure, and manage FastAPI applications.")


@fastapi_app.command(
    "create", help="Create a new FastAPI project template.", no_args_is_help=True
)
def create_fastapi(name: str):
    from volt.stacks.fastapi.app_creator import create_fastapi_app

    create_fastapi_app(name)
