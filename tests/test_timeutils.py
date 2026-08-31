"""Timezone conversion.

The reason these exist: a wrong offset here is invisible. Events still appear,
still sort correctly, still look plausible — they're just an hour or two off.
"""

from datetime import datetime, timezone

from app.timeutils import to_utc, utc_now


def test_naive_summer_datetime_is_read_as_munich_local():
    # 18:30 CEST (UTC+2) is 16:30 UTC.
    assert to_utc(datetime(2026, 9, 1, 18, 30)) == datetime(
        2026, 9, 1, 16, 30, tzinfo=timezone.utc
    )


def test_naive_winter_datetime_uses_the_winter_offset():
    # 18:30 CET (UTC+1) is 17:30 UTC. A hardcoded +02:00 would fail here, which
    # is the whole point of using ZoneInfo instead of a fixed offset.
    assert to_utc(datetime(2026, 1, 15, 18, 30)) == datetime(
        2026, 1, 15, 17, 30, tzinfo=timezone.utc
    )


def test_aware_datetime_is_converted_not_reinterpreted():
    # Already carries an offset, so it must be converted rather than treated as
    # Munich local time — otherwise a client sending correct UTC gets shifted.
    already_utc = datetime(2026, 9, 1, 16, 30, tzinfo=timezone.utc)
    assert to_utc(already_utc) == already_utc


def test_to_utc_always_returns_an_aware_datetime():
    assert to_utc(datetime(2026, 9, 1, 18, 30)).tzinfo is not None


def test_utc_now_is_aware():
    # A naive now() compared against aware stored values raises TypeError at
    # runtime — this is the guard against that regression.
    assert utc_now().tzinfo is not None
