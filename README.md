![Tests Status](https://github.com/mreiche/python-streams/actions/workflows/tests.yml/badge.svg)
[![Code Coverage Status](https://codecov.io/github/mreiche/python-streams/branch/main/graph/badge.svg)](https://app.codecov.io/github/mreiche/python-streams)

# tinystream / python-streams

This is a simple and lightweight Streams API inspired by Java Streams with support for type hinting.

This package is release as `tinystream` at pypi.

## Basic API

```python
from tinystream import Stream

stream = Stream.of([1, 2, 3, 4, 5]) # of_many(*), of_dict()

stream \
    .map(lambda x: x + 1) \       # flatmap(), peek(), map_key()
    .filter(lambda x: x > 2) \    # filter_key()
    .sorted(int, reverse=True) \  # sort()
    .reverse() \                  # collect(), count()
    .limit(2) \
    .concat([4]) \
    .sum()                        # reduce(), max(), min()
```


## Built-in Optional support

Aggregator functions are *optional*:
```python
assert Stream.of((1, 2, 3, 4, 5)).sum().is_empty == False
```

Get next value as *optional*:
```python
Stream.of((1, 2, 3, 4, 5)).next().is_empty = False
```

Create custom *optional*:
```python
from tinystream import Opt

assert Opt(None).is_empty is True
```

Map optional:
```python
assert Opt("String").map(len).get() == 6
```

Get default value:
```python
assert Opt(None).get(6) == 6
assert Opt(None).get(lambda: 6) == 6
```

Filter value:
```python
assert Opt(0).filter(lambda x: x > 0).is_empty is True
```

## Typehinting

You can typehint datatypes like:

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
assert stream.map(lambda x: x.parent, typehint=Node).next().get().name == "B"
```

This is not necessary when you pass a mapping function:
```python
def map_parent(n: Node):
    return n.parent

assert stream.map(map_parent).next().get().name == "B"
```

### Typed dictionaries

Dictionaries are streamed as `tuple(key, value)`

```python
children = {"a": Node(name="Child")} 
stream = Stream.of_dict(children)
for item in stream:
    # item[0] is known as str
    # item[1] is known as Node
```

This is the same like (but without known types):
```python
stream = Stream.of(children)
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
