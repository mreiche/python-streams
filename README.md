![Tests Status](https://github.com/mreiche/python-streams/actions/workflows/tests.yml/badge.svg)
[![Code Coverage Status](https://codecov.io/github/mreiche/python-streams/branch/main/graph/badge.svg)](https://app.codecov.io/github/mreiche/python-automation-framework)

# tinystream / python-streams

This is a simple and lightweight Streams API inspired by Java Streams with support for type hinting.

This package is release as `tinystream` at pypi.

## Basic API

```python
from tinystream import Stream

stream = Stream.of([1, 2, 3, 4, 5]) # of_many(*), of_dict()

stream \
    .map(lambda x: x + 1) \       # flatmap(), each(), next(), peek(), map_key()
    .filter(lambda x: x > 2) \    # filter_key()
    .sorted(int, reverse=True) \  # sort()
    .reverse() \                  # collect(), count()
    .limit(2) \
    .concat([4]) \
    .sum()                        # first, reduce(), max(), min()
```

## Typehinting

Since Python does not support typed lambdas, this library implements a workaround.

```python
from tinystream import Stream

stream = Stream.of(["A", "B", "C"], str)
```

This is not necessary when typing is used:

```python
from tinystream import Stream
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
parent = Node(name="B")
child = Node(name="A", parent=parent)

stream = Stream.of([child])
assert stream.map(lambda x: x.parent, typehint=Node).next().name == "B"
```

This is not necessary when you pass a mapping function:
```python
def map_parent(n: Node):
    return n.parent

assert stream.map(map_parent).next().name == "B"
```

## Retrieve optional

The `first` property returns a [optional.py:Optional](https://pypi.org/project/optional.py/) 

```python
stream.first.is_present()
```

## End of stream

Calling methods like `sum()`, `collect()`, `count()`... will end the stream.

## More features

### Filter by existing key
```python
items_with_name = Stream.of([child]).filter_key("name")
```

### Map object name attribute
```python
names = Stream.of([child]).map_key("name")
```

### Deep mapping of name attributes
```python
list = [
   {"node": Node(name="Node A")},
   {"node": Node(name="Node B")},
   {"node": Node(name="Node C")},
   {"node": Node(name="Node D")},
]
Stream.of(list).map_keys(("node", "name"))
```

### Collected join

```python
all_names = Stream.of([child]).map_key("name").join(", ")
```

### Stream dictionaries

Dictionaries are streamed as `tuple(key, value)`

```python
children = {"a": child} 
stream = Stream.of_dict(children)
values = stream.map_key(1, typehint=Node)
```

## Comparison with other libraries

There are a couple of other implementation to fulfill similar requirements.

- https://github.com/alemazzo/Python-Java-Stream
- https://github.com/ramsteak/streams
- https://pypi.org/project/fluentpy
- https://github.com/JaviOverflow/python-streams (*outdated*)
- https://github.com/9seconds/streams/ (*outdated*)
- https://github.com/tolsac/streampy (*outdated*)
- Apache Spark

## Run the tests

```shell
PYTHONPATH="." pytest --cov=tinystream -n 4 tests/
```

### Release update
1. Update version in `setup.py`
2. Package library
    ```shell
    python setup.py sdist
    ```
3. Publish library
    ```shell
    twine upload dist/tinystream-[version].tar.gz
    ```

## References

- https://github.com/MichaelKim0407/tutorial-pip-package
- https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
