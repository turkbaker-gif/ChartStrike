from datetime import datetime, time
import pytz


def is_hk_market_open() -> bool:
    """Check if Hong Kong market is currently open (09:30–12:00, 13:00–16:00 HKT)."""
    hkt = pytz.timezone("Asia/Hong_Kong")
    now = datetime.now(hkt)
    weekday = now.weekday()  # Monday=0, Sunday=6
    if weekday >= 5:  # Saturday/Sunday
        return False

    current_time = now.time()
    morning_start = time(6, 30)
    morning_end = time(12, 0)
    afternoon_start = time(13, 0)
    afternoon_end = time(16, 0)

    return (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end)


def is_cn_market_open() -> bool:
    """Check if China A-share market is open (09:30–11:30, 13:00–15:00 CST)."""
    cst = pytz.timezone("Asia/Shanghai")
    now = datetime.now(cst)
    weekday = now.weekday()
    if weekday >= 5:
        return False

    current_time = now.time()
    morning_start = time(6, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)

    return (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end)


def is_any_target_market_open() -> bool:
    """Return True if either HK or CN market is open."""
    return is_hk_market_open() or is_cn_market_open()