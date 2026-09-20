"""
Back-of-the-envelope estimator — the toolkit from HLD Chapter 1 & 12, in code.

This is NOT something you'd run in an interview (you do it on paper). It's here
so you can check your own arithmetic while practicing the estimate step.

    python3 estimate.py
"""

SECONDS_PER_DAY = 100_000  # the rounding trick: 86,400 -> 100,000


def per_second(daily_total: float) -> float:
    """The core move: daily total -> per-second rate."""
    return daily_total / SECONDS_PER_DAY


def human_bytes(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(n) < 1000:
            return f"{n:.1f} {unit}"
        n /= 1000
    return f"{n:.1f} EB"


def estimate(name: str, writes_per_day: float, read_write_ratio: float,
             bytes_per_record: float) -> None:
    writes_sec = per_second(writes_per_day)
    reads_sec = writes_sec * read_write_ratio
    storage_day = writes_per_day * bytes_per_record
    storage_year = storage_day * 365

    print(f"=== {name} ===")
    print(f"  writes/sec:   {writes_sec:,.0f}")
    print(f"  reads/sec:    {reads_sec:,.0f}  (ratio {read_write_ratio:.0f}:1)")
    print(f"  new storage:  {human_bytes(storage_day)}/day  "
          f"-> {human_bytes(storage_year)}/year")

    # Quick design hints based on the numbers (the WHOLE point of estimating).
    if reads_sec > 10_000:
        print("  -> reads are heavy: add a CACHE + read REPLICAS.")
    if storage_year > 4_000 * 1e9:  # > ~4 TB/year (one disk)
        print("  -> data outgrows one disk: will need SHARDING.")
    if writes_sec < 100 and storage_year < 1e12:
        print("  -> modest load: a single replicated DB is plenty. Don't over-build.")
    print()


if __name__ == "__main__":
    # URL shortener (Ch 1): 1M URLs/day, 100:1 reads, 500 B/record
    estimate("URL shortener", 1_000_000, 100, 500)

    # URL shortener at scale (Ch 12): 100M/day
    estimate("URL shortener @ scale", 100_000_000, 100, 500)

    # Twitter feed (Ch 13): 600M tweets/day, ~5:1 at timeline level, 300 B
    estimate("Twitter tweets", 600_000_000, 5, 300)

    # Chat (Ch 14): 100B messages/day, ~1:1, 100 B
    estimate("Chat messages", 100_000_000_000, 1, 100)
