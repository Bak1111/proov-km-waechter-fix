# fleet_utils.py
# Utility helpers for KM-Waechter. Modernized 2024.
# Dead code removed: is_due(), parse_service_date(), chunk_list(), mean()
# were all unreferenced; is_due() also duplicated km_wachter.needs_service logic.

MILES_PER_KM = 0.621371  # corrected from 1.609 (that was km-per-mile, not miles-per-km)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"
