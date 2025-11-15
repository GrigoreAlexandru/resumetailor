"""Entry point for python -m resume_tailor."""
from .cli.commands import app
from .config.settings import settings
from .utils.logger import setup_logging


def main() -> None:
    """Main entry point."""
    setup_logging(settings.log_level)
    app()


if __name__ == "__main__":
    main()
