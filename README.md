# python-streams

This is a simple Streams API inspired by Java Streams with type hints support.

## Basic API

```python
from streams import Stream

stream = Stream.of([1, 2, 3, 4, 5]) # of_many(*), of_dict()

stream \
    .map(lambda x: x + 1) \       # flat_map(), each(), next(), peek()
    .filter(lambda x: x > 2) \
    .sorted(int, reverse=True) \  # sort()
    .reverse() \                  # collect(), count()
    .limit(2) \
    .concat([4]) \
    .sum()                        # reduce(), max(), min()
```
## Typehints

Since Python does not support typed lambdas, this library implements a workaround.

```python
from streams import Stream

stream = Stream.of(["A", "B", "C"], str)
```

This is not necessary when typing is used:

```python
from streams import Stream
from typing import List

list: List[str] = ["A", "B", "C"]
stream = Stream.of(list)
```

Type hinting the given type:

```python
from dataclasses import dataclass

@dataclass
class Node:
    name: str
    parent: "Node" = None
```

for lambdas:

```python
from streams import Stream

parent = Node(name="B")
child = Node(name="A", parent=parent)

stream = Stream.of([child])
assert stream.map(lambda x: x.parent, Node).next().name == "B"
```

This is not necessary when you pass a mapping function:
```python
def map_parent(n: Node):
    return n.parent

assert stream.map(map_parent).next().name == "B"
```



## Comparison with other libraries

There are a couple of other implementation to fulfill similar requirements.

- https://github.com/alemazzo/Python-Java-Stream
- https://github.com/ramsteak/streams
- https://pypi.org/project/fluentpy/
- Apache Spark

## Run the tests

```shell
PYTHONPATH="." pytest --cov=src tests/
```
