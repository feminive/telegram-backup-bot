from tg_media_archiver.archiver import MediaArchiver
from tg_media_archiver.config import Settings


def test_slug_filename_preserves_extension() -> None:
    settings = Settings.model_construct(
        telegram_api_id=1,
        telegram_api_hash="hash",
        telegram_channel="@channel",
        rclone_remote="remote:path",
    )
    archiver = MediaArchiver(settings)
    assert archiver._slug_filename("my file!!.mp4") == "my-file.mp4"
