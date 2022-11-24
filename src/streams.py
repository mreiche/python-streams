import functools
from typing import Iterable, Generic, TypeVar, Callable, ClassVar, List, Iterator, Dict, Tuple

T = TypeVar("T")
R = TypeVar("R")
K = TypeVar("K")


class Stream:

    @staticmethod
    def of(iterable: Iterable[T], typehint: T = None):
        return IterableStream[T](iterable)

    @staticmethod
    def ofDict(dict: Dict[K, T]):
        return IterableStream[Tuple[K,T]](dict)


class IterableStream(Generic[T]):
    def __flatmap(self, f, xs):
        return (y for ys in xs for y in f(ys))

    def __init__(self, iterable: Iterable[T]):
        if isinstance(iterable, Iterator):
            self.__iterable = iterable
            self.__collected: List[T] = None
        elif isinstance(iterable, list):
            self.__iterable = iter(iterable)
            self.__collected = iterable
        elif isinstance(iterable, dict):
            self.__iterable = iter(iterable.items())
        elif isinstance(iterable, str):
            self.__iterable = iter(iterable)

    def map(self, cb: Callable[[T], R], typehint: R = None):
        return IterableStream[R](map(cb, self.__iterable))

    def filter(self, cb: Callable[[T], R], typehint: R = None):
        return IterableStream[R](filter(cb, self.__iterable))

    def flatmap(self, cb: Callable[[T], Iterable[R]], typehint: R = None):
        return IterableStream[R](self.__flatmap(cb, self.__iterable))

    def peak(self, cb: Callable[[T], None]):
        def __peak(x: T):
            cb(x)
            return x

        return IterableStream[T](map(__peak, self.__iterable))

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
