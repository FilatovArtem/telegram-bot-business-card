from aiogram.types import CallbackQuery, Message


def cb_message(callback: CallbackQuery) -> Message:
    """Narrow type: after inline keyboard render message is always Message."""
    msg = callback.message
    if not isinstance(msg, Message):
        raise RuntimeError("callback.message is None or InaccessibleMessage")
    return msg


def cb_data(callback: CallbackQuery) -> str:
    """Narrow type: after F.data.* filter data is guaranteed to be str."""
    data = callback.data
    if data is None:
        raise RuntimeError("callback.data is None")
    return data


def cb_int(data: str, idx: int) -> int | None:
    """Safely extract int from callback_data like `prefix:N` or `prefix:X:N`.
    Returns None if parsing fails (no crash)."""
    parts = data.split(":")
    if idx >= len(parts):
        return None
    try:
        return int(parts[idx])
    except ValueError:
        return None
