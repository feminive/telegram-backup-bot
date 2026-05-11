import asyncio
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.custom.message import Message

from .config import Settings
from .storage import ArchiveStore, ArchivedMessage
from .uploader import RcloneUploader


logger = logging.getLogger(__name__)
SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


class MediaArchiver:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = ArchiveStore(settings.database_path)
        self.uploader = RcloneUploader(settings.rclone_remote, settings.rclone_extra_args)
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_uploads)
        self.client = TelegramClient(
            settings.telegram_session_name,
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )

    async def run(self) -> None:
        await self.client.start()
        entity = await self.client.get_entity(self.settings.telegram_channel)
        channel_id = getattr(entity, "id", self.settings.telegram_channel)
        logger.info("Listening to %s", self.settings.telegram_channel)

        if self.settings.history_limit > 0:
            logger.info("Backfilling last %s messages", self.settings.history_limit)
            async for message in self.client.iter_messages(entity, limit=self.settings.history_limit):
                await self._process_message(message)

        @self.client.on(events.NewMessage(chats=entity))
        async def handler(event: events.NewMessage.Event) -> None:
            await self._process_message(event.message)

        logger.debug("Resolved channel id: %s", channel_id)
        await self.client.run_until_disconnected()

    async def _process_message(self, message: Message) -> None:
        if not message.media:
            return
        chat_id = message.chat_id or 0
        message_id = message.id
        if self.store.is_archived(chat_id, message_id):
            return
        async with self.semaphore:
            await self._download_and_upload(message, chat_id, message_id)

    async def _download_and_upload(self, message: Message, chat_id: int, message_id: int) -> None:
        timestamp = message.date.astimezone(timezone.utc) if message.date else datetime.now(timezone.utc)
        channel_slug = self._slug(str(message.chat.title if message.chat else chat_id))
        original_name = self._extract_filename(message)
        local_dir = self.settings.telegram_download_dir / channel_slug / timestamp.strftime("%Y") / timestamp.strftime("%m")
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / original_name

        logger.info("Downloading media from chat=%s message=%s", chat_id, message_id)
        downloaded = await message.download_media(file=local_path)
        if not downloaded:
            raise RuntimeError(f"Failed to download media from message {message_id}")

        remote_path = self.settings.rclone_path_template.format(
            channel=channel_slug,
            year=timestamp.strftime("%Y"),
            month=timestamp.strftime("%m"),
            filename=Path(downloaded).name,
        )
        await self.uploader.upload(Path(downloaded), remote_path)
        self.store.mark_archived(
            ArchivedMessage(
                chat_id=chat_id,
                message_id=message_id,
                local_path=str(downloaded),
                remote_path=remote_path,
            )
        )
        logger.info("Archived media from message=%s to %s", message_id, remote_path)

    def _extract_filename(self, message: Message) -> str:
        file_name = None
        if message.file and message.file.name:
            file_name = message.file.name
        elif message.file and message.file.ext:
            file_name = f"message-{message.id}{message.file.ext}"
        else:
            file_name = f"message-{message.id}.bin"
        return self._slug_filename(file_name)

    def _slug_filename(self, value: str) -> str:
        path = Path(value)
        stem = SAFE_NAME.sub("-", path.stem).strip("-") or "file"
        suffix = SAFE_NAME.sub("", path.suffix) or ".bin"
        return f"{stem}{suffix}"

    def _slug(self, value: str) -> str:
        return SAFE_NAME.sub("-", value).strip("-").lower() or "channel"
