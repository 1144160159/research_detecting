"""Bounded batching helpers that never consume beyond the requested limit."""

from __future__ import annotations

from typing import Iterable, Iterator, List, TypeVar


T = TypeVar("T")


def bounded_batches(
    iterable: Iterable[T],
    batch_size: int,
    max_items: int = 0,
) -> Iterator[List[T]]:
    """Yield batches without pulling an item beyond ``max_items``.

    ``max_items=0`` means unbounded.  Avoiding the conventional ``for`` loop
    matters for stateful readers: a loop retrieves the next item before its
    body can check the limit, which otherwise inflates PCAP reader statistics
    by one packet.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if max_items < 0:
        raise ValueError("max_items must be non-negative")

    iterator = iter(iterable)
    emitted = 0
    while max_items == 0 or emitted < max_items:
        remaining = (
            batch_size
            if max_items == 0
            else min(batch_size, max_items - emitted)
        )
        batch: List[T] = []
        for _ in range(remaining):
            try:
                item = next(iterator)
            except StopIteration:
                break
            batch.append(item)
            emitted += 1
        if batch:
            yield batch
        if len(batch) < remaining:
            break
