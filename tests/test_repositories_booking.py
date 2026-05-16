import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import (
    create_booking,
    get_bookings_by_status,
    update_booking_status,
    upsert_user,
)


async def _create_test_user(session: AsyncSession, user_id: int = 9001) -> None:
    await upsert_user(session, user_id=user_id, full_name="Test User", username=None)


@pytest.mark.asyncio
async def test_create_booking_default_status_is_new(session: AsyncSession) -> None:
    await _create_test_user(session)

    booking = await create_booking(
        session,
        user_id=9001,
        service="Медовик",
        client_name="Иван",
        phone="+79991234567",
        desired_date="15 июня",
    )

    assert booking.status == "new"
    assert booking.id is not None


@pytest.mark.asyncio
async def test_update_booking_status_persists(session: AsyncSession) -> None:
    await _create_test_user(session)
    booking = await create_booking(
        session,
        user_id=9001,
        service="Медовик",
        client_name="Иван",
        phone="+79991234567",
        desired_date="15 июня",
    )

    updated = await update_booking_status(session, booking.id, "confirmed")

    assert updated is not None
    assert updated.status == "confirmed"
    assert updated.id == booking.id


@pytest.mark.asyncio
async def test_update_booking_status_returns_none_for_missing_id(session: AsyncSession) -> None:
    result = await update_booking_status(session, booking_id=99999, status="confirmed")

    assert result is None


@pytest.mark.asyncio
async def test_get_bookings_by_status_filters_correctly(session: AsyncSession) -> None:
    await _create_test_user(session)
    b1 = await create_booking(
        session,
        user_id=9001,
        service="Медовик",
        client_name="Иван",
        phone="+79991234567",
        desired_date="15 июня",
    )
    b2 = await create_booking(
        session,
        user_id=9001,
        service="Торт",
        client_name="Мария",
        phone="+79991234568",
        desired_date="20 июня",
    )
    await update_booking_status(session, b1.id, "confirmed")
    # b2 stays "new"

    new_bookings = await get_bookings_by_status(session, "new")
    confirmed_bookings = await get_bookings_by_status(session, "confirmed")

    new_ids = {b.id for b in new_bookings}
    confirmed_ids = {b.id for b in confirmed_bookings}

    assert b2.id in new_ids
    assert b1.id not in new_ids
    assert b1.id in confirmed_ids
    assert b2.id not in confirmed_ids


@pytest.mark.asyncio
async def test_get_bookings_by_status_ordered_desc_by_created_at(session: AsyncSession) -> None:
    await _create_test_user(session)
    b1 = await create_booking(
        session, user_id=9001, service="A", client_name="A", phone="+79991234567", desired_date="1 июня"
    )
    b2 = await create_booking(
        session, user_id=9001, service="B", client_name="B", phone="+79991234568", desired_date="2 июня"
    )

    bookings = await get_bookings_by_status(session, "new")

    # Ordered desc: newer booking (b2) must come first
    ids = [b.id for b in bookings]
    assert ids.index(b2.id) < ids.index(b1.id)
