import functools, itertools
from typing import Iterable, Generic, TypeVar, Callable, ClassVar, List, Iterator, Dict, Tuple

T = TypeVar("T")
R = TypeVar("R")
K = TypeVar("K")


class Stream:

    @staticmethod
    def of(iterable: Iterable[T], typehint: T = None):
        return IterableStream[T](iterable)

    @staticmethod
    def of_dict(source_dict: Dict[K, T]):
        return IterableStream[Tuple[K,T]](source_dict)

    @staticmethod
    def of_many(typehint: T = None, *iterables):
        return IterableStream[T]([]).concat(iterables)


class IterableStream(Generic[T]):

    def __normalize_iterator(self, iterable: Iterable[T]):
        if isinstance(iterable, Iterator):
            return iterable
        elif isinstance(iterable, list):
            return iter(iterable)
        elif isinstance(iterable, dict):
            return iter(iterable.items())
        elif isinstance(iterable, str):
            return iter(iterable)


    def __init__(self, iterable: Iterable[T]):
        self.__iterable = self.__normalize_iterator(iterable)
        self.__collected: List[T] = None


    def map(self, cb: Callable[[T], R], typehint: R = None):
        return IterableStream[R](map(cb, self.__iterable))

    def filter(self, cb: Callable[[T, T], bool]):
        return IterableStream[T](filter(cb, self.__iterable))

    def flatmap(self, cb: Callable[[T], Iterable[R]], typehint: R = None):
        def __flatmap(f, xs):
            return (y for ys in xs for y in f(ys))

        return IterableStream[R](__flatmap(cb, self.__iterable))

    def peek(self, cb: Callable[[T], None]):
        def __peek(x: T):
            cb(x)
            return x

        return IterableStream[T](map(__peek, self.__iterable))

    def sort(self, compare: Callable[[T, T], bool], reverse: bool = False):
        key = functools.cmp_to_key(compare)
        sort = sorted(self.__iterable, key=key, reverse=reverse)
        return IterableStream[T](sort)

    def each(self) -> Iterable[T]:
        return self.__iterable

    def one(self) -> T|None:
        try:
            return next(self.__iterable)
        except StopIteration as e:
            return None

    def collect(self):
        if not self.__collected:
            self.__collected = list(self.__iterable)
        return self.__collected

    def count(self):
        return len(self.collect())

    def reverse(self):
        copy = self.collect().copy()
        copy.reverse()
        return IterableStream[T](copy)

    def reduce(self, cb: Callable[[T, T], R]) -> R:
        return functools.reduce(cb, self.__iterable)

    def sum(self) -> T:
        return self.reduce(lambda x, y: x + y)

    def max(self) -> T:
        return self.reduce(lambda x, y: x if x > y else y)

    def min(self) -> T:
        return self.reduce(lambda x, y: x if x < y else y)

    def limit(self, limit: int):
        def __limit():
           for i in range(limit):
               yield self.one()

        return IterableStream[T](__limit())

    def concat(self, *iterables):
        iterators = []
        for iterator in iterables:
            iterators.append(self.__normalize_iterator(iterator))

        return IterableStream[T](itertools.chain(*iterators))
