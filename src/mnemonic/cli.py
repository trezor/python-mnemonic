import sys

import click

from mnemonic import Mnemonic
from mnemonic.mnemonic import ConfigurationError


@click.group()
def cli() -> None:
    """BIP-39 mnemonic phrase generator and validator."""
    pass


@cli.command()
@click.option(
    "-l",
    "--language",
    default="english",
    type=str,
    help="Language for the mnemonic wordlist.",
)
@click.option(
    "-s",
    "--strength",
    default="128",
    type=click.Choice(["128", "160", "192", "224", "256"]),
    help="Entropy strength in bits.",
)
@click.option(
    "-p",
    "--passphrase",
    default="",
    envvar="MNEMONIC_PASSPHRASE",
    type=str,
    help="Passphrase for seed derivation. Can also be set via MNEMONIC_PASSPHRASE env var.",
)
@click.option(
    "-P",
    "--prompt-passphrase",
    is_flag=True,
    default=False,
    help="Prompt for passphrase with hidden input (secure).",
)
@click.option(
    "--hide-seed",
    is_flag=True,
    default=False,
    help="Do not display the derived seed.",
)
def create(
    language: str,
    passphrase: str,
    prompt_passphrase: bool,
    strength: str,
    hide_seed: bool,
) -> None:
    """Generate a new mnemonic phrase and its derived seed."""
    if prompt_passphrase:
        if passphrase:
            click.secho(
                "Warning: --prompt-passphrase overrides -p/MNEMONIC_PASSPHRASE.",
                fg="yellow",
                err=True,
            )
        passphrase = click.prompt("Passphrase", default="", hide_input=True)
    try:
        mnemo = Mnemonic(language)
        words = mnemo.generate(int(strength))
        click.echo(f"Mnemonic: {words}")
        if not hide_seed:
            seed = mnemo.to_seed(words, passphrase)
            click.echo(f"Seed: {seed.hex()}")
    except ConfigurationError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.option(
    "-l",
    "--language",
    default=None,
    type=str,
    help="Language for the mnemonic wordlist. Auto-detected if not specified.",
)
@click.argument("words", nargs=-1)
def check(language: str | None, words: tuple[str, ...]) -> None:
    """Validate a mnemonic phrase's checksum.

    WORDS can be provided as arguments or piped via stdin.
    """
    if words:
        mnemonic = " ".join(words)
    else:
        mnemonic = sys.stdin.read().strip()

    if not mnemonic:
        raise click.ClickException("No mnemonic provided.")

    try:
        if language is None:
            language = Mnemonic.detect_language(mnemonic)
        mnemo = Mnemonic(language)
        if mnemo.check(mnemonic):
            click.secho("Valid mnemonic.", fg="green")
        else:
            raise click.ClickException("Invalid mnemonic checksum.")
    except ConfigurationError as e:
        raise click.ClickException(str(e))
    except (ValueError, LookupError) as e:
        raise click.ClickException(str(e))


@cli.command("to-seed")
@click.option(
    "-p",
    "--passphrase",
    default="",
    envvar="MNEMONIC_PASSPHRASE",
    type=str,
    help="Passphrase for seed derivation. Can also be set via MNEMONIC_PASSPHRASE env var.",
)
@click.option(
    "-P",
    "--prompt-passphrase",
    is_flag=True,
    default=False,
    help="Prompt for passphrase with hidden input (secure).",
)
@click.argument("words", nargs=-1)
def to_seed(passphrase: str, prompt_passphrase: bool, words: tuple[str, ...]) -> None:
    """Derive a seed from a mnemonic phrase.

    WORDS can be provided as arguments or piped via stdin.
    Outputs the 64-byte seed in hexadecimal format.
    """
    if words:
        mnemonic = " ".join(words)
    else:
        mnemonic = sys.stdin.read().strip()

    if not mnemonic:
        raise click.ClickException("No mnemonic provided.")

    if prompt_passphrase:
        if passphrase:
            click.secho(
                "Warning: --prompt-passphrase overrides -p/MNEMONIC_PASSPHRASE.",
                fg="yellow",
                err=True,
            )
        passphrase = click.prompt("Passphrase", default="", hide_input=True)

    try:
        language = Mnemonic.detect_language(mnemonic)
        mnemo = Mnemonic(language)
        if not mnemo.check(mnemonic):
            raise click.ClickException("Invalid mnemonic checksum.")
        seed = mnemo.to_seed(mnemonic, passphrase)
        click.echo(seed.hex())
    except ConfigurationError as e:
        raise click.ClickException(str(e))
    except (ValueError, LookupError) as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
