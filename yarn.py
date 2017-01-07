import sys
from collections.abc import Sequence
from itertools import islice

__all__ = ('yarn', )

EMPTY = object()


class yarn:
    in_memory_types = (Sequence, )

    def __init__(self, iterable):
        # Better fail here than in a runtime
        iter(iterable)

        if isinstance(iterable, self.in_memory_types):
            self.cache = iterable
            self.iterable = ()
            self.is_cached = True
            self.is_clone = False
        else:
            self.cache = []
            self.iterable = iterable
            self.is_cached = False
            self.is_clone = isinstance(iterable, yarn)

    def __iter__(self):
        if self.is_cached:
            return (yield from self.cache)

        # First returns cached
        yield from self.cache

        # Then goes to source
        cache_from = len(self.cache)
        for index, x in enumerate(self.iterable):
            # If yarn is a clone of another
            # it will receive parents cache first,
            # which may produce duplicates since it has own one.
            # Then it should seek until it gets a new data.
            # But if starts with a real generator it must cache everything.

            if not self.is_clone or index >= cache_from:
                self.cache.append(x)
                yield x

        self.is_cached = True

    def __getitem__(self, key):
        is_slice = isinstance(key, slice)

        if not self.is_cached:
            if not is_slice:
                stop = key
            else:
                try:
                    return yarn(islice(self, key.start, key.stop, key.step))
                except ValueError:
                    # Negative indexing
                    if key.step and key.step < 0:
                        stop = key.start or sys.maxsize
                    else:
                        stop = key.stop or sys.maxsize

            # Caches self till the index is reached
            # or pushes everything if negative indexed
            for index, x in enumerate(self):
                if index == stop:
                    break

        if is_slice:
            return yarn(self.cache[key])

        # Index access
        return self.cache[key]

    def __len__(self):
        if not self.is_cached:
            return sum(1 for x in self)
        return len(self.cache)

    def __bool__(self):
        return next(iter(self), EMPTY) is not EMPTY

    def __repr__(self):
        return '<yarn {!r}>'.format(self.cache)
