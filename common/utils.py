import random
import string
from itertools import chain, islice
from typing import Iterable, List


def chunks(iterable: Iterable, size=10) -> List[Iterable]:
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


def random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
