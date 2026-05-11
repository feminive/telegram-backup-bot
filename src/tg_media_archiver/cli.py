import asyncio
import logging

from .archiver import MediaArchiver
from .config import Settings


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    settings = Settings()
    settings.ensure_directories()
    configure_logging(settings.log_level)
    archiver = MediaArchiver(settings)
    asyncio.run(archiver.run())


if __name__ == "__main__":
    main()
