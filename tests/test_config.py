import pytest

from bot.config import Settings


def test_settings_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_IDS", raising=False)

    s = Settings(
        _env_file=None,  # type: ignore[call-arg]
        bot_token="123456789:AABBCCDDEEFFaabbccddeeff",
        admin_ids="1,2,3",
    )

    assert s.admin_ids == [1, 2, 3]
    assert isinstance(s.admin_ids, list)
    assert ":" in s.bot_token


def test_settings_missing_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_IDS", raising=False)

    with pytest.raises((ValueError, Exception)):
        Settings(
            _env_file=None,  # type: ignore[call-arg]
            admin_ids="42",
        )


def test_settings_malformed_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_IDS", raising=False)

    # Token without colon and too short — must fail validation
    with pytest.raises(ValueError, match="BOT_TOKEN"):
        Settings(
            _env_file=None,  # type: ignore[call-arg]
            bot_token="shorttoken",
            admin_ids="42",
        )


def test_settings_empty_admin_ids_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_IDS", raising=False)

    with pytest.raises(ValueError, match="ADMIN_IDS"):
        Settings(
            _env_file=None,  # type: ignore[call-arg]
            bot_token="123456789:AABBCCDDEEFFaabbccddeeff",
            admin_ids="",
        )
