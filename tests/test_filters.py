from unittest.mock import MagicMock

import pytest

from bot.filters import AdminFilter


def _make_message(user_id: int | None) -> MagicMock:
    msg = MagicMock()
    if user_id is None:
        msg.from_user = None
    else:
        msg.from_user = MagicMock()
        msg.from_user.id = user_id
    return msg


@pytest.mark.asyncio
async def test_admin_filter_allows_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    import bot.filters as filters_module

    monkeypatch.setattr(filters_module.settings, "admin_ids", [100, 200])

    f = AdminFilter()
    msg = _make_message(100)
    result = await f(msg)

    assert result is True


@pytest.mark.asyncio
async def test_admin_filter_blocks_non_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    import bot.filters as filters_module

    monkeypatch.setattr(filters_module.settings, "admin_ids", [100, 200])

    f = AdminFilter()
    msg = _make_message(999)
    result = await f(msg)

    assert result is False


@pytest.mark.asyncio
async def test_admin_filter_blocks_anonymous(monkeypatch: pytest.MonkeyPatch) -> None:
    import bot.filters as filters_module

    monkeypatch.setattr(filters_module.settings, "admin_ids", [100, 200])

    f = AdminFilter()
    msg = _make_message(None)
    result = await f(msg)

    assert result is False
