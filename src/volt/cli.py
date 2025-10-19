from typer import Typer

from volt.stacks.fastapi import create_fastapi_app

app = Typer(help="An extremely fast template manager")

fastapi_app = Typer(help="FastAPI tools")
app.add_typer(fastapi_app, name="fastapi")


@fastapi_app.command("create")
def create_fastapi(name: str):
    create_fastapi_app(name)


def main():
    app()


if __name__ == "__main__":
    main()
