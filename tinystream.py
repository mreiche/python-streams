import functools
import itertools
import logging
from typing import Iterable, TypeVar, Callable, List, Dict, Tuple, Iterator, Generic, Type
from warnings import warn

T = TypeVar("T")
R = TypeVar("R")
K = TypeVar("K")


Mapper = Callable[[T], R]
FlatMapper = Callable[[T], Iterable[R]]
Consumer = Callable[[T], None]
Comparator = Callable[[T, T], bool]
Reducer = Callable[[T, T], R]
Predicate = Callable[[T], bool]
Supplier = Callable[[], T]


def _filter_key(x: any, key: any, invert: bool = False):
    if isinstance(x, (list, tuple)):
        size = len(x)
        if invert:
            return key >= size
        else:
            return key < size
    elif isinstance(x, (dict, Iterable)):
        if invert:
            return key not in x
        else:
            return key in x
    else:
        if invert:
            return not hasattr(x, key)
        else:
            return hasattr(x, key)


def _map_key(x: any, key: any):
    if isinstance(x, (list, dict, tuple)):
        return x[key]
    else:
        return getattr(x, key)


class Opt(Generic[T]):
    def __init__(self, value: T):
        self.__val = value

    @property
    def empty(self):
        warn("Please use absent property instead", DeprecationWarning)
        return self.absent

    @property
    def absent(self):
        return self.__val is None

    @property
    def present(self):
        return not self.absent

    def get(self, *args) -> T:
        if not self.empty:
            return self.__val
        elif len(args) > 0:
            if isinstance(args[0], Callable):
                return args[0]()
            else:
                return args[0]
        else:
            raise Exception("Cannot get value of empty Opt without default value")

    def if_present(self, consumer: Consumer[T]):
        if not self.empty:
            consumer(self.get())

    def filter(self, predicate: Predicate[T]):
        if predicate(self.__val):
            return self
        else:
            return EmptyOpt()

    def map(self, mapper: Mapper[T, R]):
        return Opt[R](mapper(self.__val))

    def if_empty(self, supplier: any|Supplier[R]):
        warn("Please use if_absent() method instead", DeprecationWarning)
        return self.if_absent(supplier)

    def if_absent(self, supplier: any|Supplier[R]):
        if self.absent:
            if isinstance(supplier, Callable):
                return Opt[R](supplier())
            else:
                return Opt[R](supplier)
        else:
            return self

    def type(self, typehint: Type[R]) -> "Opt[R]":
        return self

    def filter_type(self, typehint: Type[R]) -> "Opt[R]":
        return self.filter(lambda x: isinstance(x, typehint))

    def filter_key(self, key: str | int, invert: bool = False):
        if _filter_key(self.__val, key, invert):
            return self
        else:
            return EmptyOpt()

    def map_key(self, key: str | int):
        if _filter_key(self.__val, key):
            return Opt(_map_key(self.__val, key))
        else:
            return EmptyOpt()

    def map_keys(self, *iterables):
        inst = self
        for key in iterables:
            inst = inst.map_key(key)
        return inst

    def stream(self):
        return Stream.of(self.__val)


class EmptyOpt(Opt[None]):
    def __init__(self):
        super().__init__(None)

    def filter(self, predicate: Predicate[T]):
        return self

    def map_key(self, key: str | int):
        return self

    def filter_key(self, key: str | int, invert: bool = False):
        return self

    @property
    def absent(self):
        return True

    def stream(self):
        return Stream.of([])


class Stream:

    @staticmethod
    def of(iterable: Iterable[T]):
        return IterableStream[T](iterable)

    @staticmethod
    def of_dict(source_dict: Dict[K, T]):
        return IterableStream[Tuple[K, T]](source_dict)

    @staticmethod
    def of_many(*iterables):
        return IterableStream([]).concat(*iterables)


class IterableStream(Iterator[T]):

    def __init__(self, iterable: Iterable[T]):
        self.__iterable = self.__normalize_iterator(iterable)
        self.__collected: List[T] = None
        self.__on_end: Callable = None

    def on_end(self, cb: Callable) -> "IterableStream[R]":
        if self.__on_end:
            raise AttributeError("on_end is immutable")
        self.__on_end = cb
        return self

    def end(self):
        if self.__on_end:
            self.__on_end()
            self.__iterable = iter([])
            self.__on_end = None

    def __next__(self) -> T | None:
        try:
            return next(self.__iterable)
        except StopIteration as e:
            self.end()
            raise e

    def __iter__(self) -> Iterator[T]:
        return self

    def __normalize_iterator(self, iterable: Iterable[T]) -> Iterable[T]:
        if isinstance(iterable, list):
            return iter(iterable)
        elif isinstance(iterable, dict):
            return iter(iterable.items())
        elif isinstance(iterable, str):
            return iter(iterable)
        else:
            return iterable

    def map(self, mapper: Mapper[T, R]):
        return IterableStream[R](map(mapper, self))

    def map_key(self, key: str | int):
        return self.filter_key(key).map(lambda x: _map_key(x, key))

    def map_keys(self, *iterables):
        inst = self
        for key in iterables:
            inst = inst.map_key(key)
        return inst

    def type(self, typehint: Type[R]) -> "IterableStream[R]":
        return self

    def filter_type(self, typehint: Type[R]) -> "IterableStream[R]":
        return self.filter(lambda x: isinstance(x, typehint))

    def filter(self, predicate: Predicate[T]):
        return IterableStream[T](filter(predicate, self.__iterable))

    def filter_key(self, key: str | int, invert: bool = False):
        return self.filter(lambda x: _filter_key(x, key, invert))

    def flatmap(self, mapper: FlatMapper[T, R] = None):

        def __flatmap(f, xs):
            return (y for ys in xs for y in f(ys))

        def __flatten(xs):
            return (y for ys in xs for y in ys)

        if mapper is not None:
            return IterableStream[R](__flatmap(mapper, self))
        else:
            return IterableStream[R](__flatten(self))

    def peek(self, consumer: Consumer[T]):
        def __peek(x: T):
            consumer(x)
            return x

        return IterableStream[T](map(__peek, self))

    def sort(self, compare: Comparator[T], reverse: bool = False):
        key = functools.cmp_to_key(compare)
        sort = sorted(self.__iterable, key=key, reverse=reverse)
        return IterableStream[T](sort)

    def sorted(self, key, reverse: bool = False):
        sort = sorted(self.__iterable, key=key, reverse=reverse)
        return IterableStream[T](sort)

    def next(self) -> Opt[T]:
        try:
            next = self.__next__()
        except StopIteration as e:
            next = None
        return Opt(next)

    def collect(self):
        """Collects all items to a list and ends the stream"""
        if not self.__collected:
            self.__collected = list(self)
        return self.__collected

    def join(self, separator: str) -> str:
        """Joins the string to the elements and ends the stream"""
        return separator.join(map(str, self))

    def count(self):
        """Collects and counts all items and ends the stream"""
        return len(self.collect())

    def reverse(self):
        copy = self.collect().copy()
        copy.reverse()
        return IterableStream[T](copy)

    def reduce(self, cb: Reducer) -> Opt[R]:
        try:
            return Opt(functools.reduce(cb, self))
        except TypeError:
            return Opt(None)

    def sum(self) -> Opt[T]:
        """Sums all numbers and ends the stream"""
        return self.reduce(lambda x, y: x + y)

    def max(self) -> Opt[T]:
        return self.reduce(lambda x, y: x if x > y else y)

    def min(self) -> Opt[T]:
        return self.reduce(lambda x, y: x if x < y else y)

    def limit(self, limit: int):
        def __limit():
            for i in range(limit):
                yield self.__next__()

        return IterableStream[T](__limit())

    def concat(self, *iterables):
        iterators = [self]
        for iterator in iterables:
            iterators.append(self.__normalize_iterator(iterator))

        return IterableStream[T](itertools.chain(*iterators))

    def find(self, predicate: Predicate[T]) -> Opt[T]:
        return self.filter(predicate).next()
