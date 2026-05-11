import asyncio
import logging
import shlex
from pathlib import Path


logger = logging.getLogger(__name__)


class RcloneUploader:
    def __init__(self, remote: str, extra_args: str = "") -> None:
        self.remote = remote
        self.extra_args = shlex.split(extra_args)

    async def upload(self, source: Path, destination: str) -> None:
        command = [
            "rclone",
            "copyto",
            str(source),
            f"{self.remote}/{destination}",
            *self.extra_args,
        ]
        logger.info("Uploading %s to %s/%s", source, self.remote, destination)
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                f"rclone upload failed for {source}: {stderr.decode().strip() or stdout.decode().strip()}"
            )
