from itertools import chain, islice
from typing import Iterable, List


def chunks(iterable: Iterable, size=10) -> List[Iterable]:
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))
