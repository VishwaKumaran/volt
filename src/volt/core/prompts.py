import questionary


def choose(prompt: str, choices: list[str], default: str | None = None) -> str:
    return questionary.select(
        prompt,
        choices=choices,
        default=default or (choices[0] if choices else None),
    ).ask()


def confirm(prompt: str, default: bool = False) -> bool:
    return questionary.confirm(prompt, default=default).ask()


def input_text(prompt: str, default: str | None = None) -> str:
    return questionary.text(prompt, default=default or "").ask()
