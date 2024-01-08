![Tests Status](https://github.com/mreiche/python-streams/actions/workflows/tests.yml/badge.svg)
[![Code Coverage Status](https://codecov.io/github/mreiche/python-streams/branch/main/graph/badge.svg)](https://app.codecov.io/github/mreiche/python-streams)

# tinystream / python-streams

This is a simple and lightweight Streams API inspired by Java Streams with support for type hinting.

This package is release as `tinystream` at pypi.

## Basic API

```python
from tinystream import Stream

stream = Stream([1, 2, 3, 4, 5])  # Stream.of_many(*), Stream.of_dict()

stream \
    .map(lambda x: x + 1) \       # flatmap(), peek(), map_key(), map_kwargs(), map_keys()
    .filter(lambda x: x > 2) \    # filter_key(), filter_type()
    .sorted(reverse=True) \       # sort()
    .reverse() \
    .limit(2) \
    .concat([4]) \
    .sum()                        # reduce(), max(), min(), collect(), count(), find()
```

## Aggregators

Aggregators like `sum()`, `count()`, `max()` will `collect()` the data and end the stream. `collect()` also caches the data and can be called multiple times, since it returns only a `list`.

## Built-in Optional support

Some aggregators like `sum()`, `max()` are *optional*:

```python
assert Stream((1, 2, 3, 4, 5)).sum().present
```

Get next value as *optional*:

```python
assert Stream((1, 2, 3, 4, 5)).next().present
```

Create custom *optional*:

```python
from tinystream import Opt

assert Opt(None).absent
```

Map *optional*:
```python
assert Opt("String").map(str.lower).len == 6
```

Get default value:
```python
assert Opt(None).get(6) == 6
assert Opt(None).get(lambda: 6) == 6
assert Opt(None).if_absent(lambda: 3).present
```

Filter value:

```python
assert Opt(0).filter(lambda x: x > 0).absent
```

You can also access optional index elements of the stream, but this will `collect()` and end the stream.
```python
assert Stream([])[2].absent
```

## Type hinting

You can typehint datatypes like:

```python
from dataclasses import dataclass

@dataclass
class Node:
    name: str
    parent: "Node" = None

parent = Node(name="B")
child = Node(name="A", parent=parent)
```

for lambdas:

```python
stream = Stream([child])
assert stream.map(lambda x: x.parent).type(Node).next().get().name == "B"
```

This is not necessary when you pass a mapping function:
```python
def map_parent(n: Node):
    return n.parent

assert stream.map(map_parent).next().get().name == "B"
```

## More features

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
stream = Stream(children)
```

### Filter by existing key
```python
items_with_name = Stream([child]).filter_key("name")
```

### Filter by type
```python
nodes_only = Stream([child]).filter_type(Node)
```

### Map object name attribute
```python
names = Stream([child]).map_key("name")
```

### Deep mapping of name attributes
```python
list = [
   {"node": Node(name="Node A")},
   {"node": Node(name="Node B")},
   {"node": Node(name="Node C")},
   {"node": Node(name="Node D")},
]
names = Stream(list).map_keys("node", "name")
```

### Collected join

```python
all_names = Stream([child]).map_key("name").join(", ")
```

### Map kwargs
```python
list = [
   {"name": "Node A"},
   {"name": "Node B"},
]
# Short cut for map(lambda x: Node(**x))
nodes = Stream(list).map_kwargs(Node)
```

### Stream many

```python
many = Stream.of_many([1, 2, 3], (4, 5, 6))
many = many.concat([7, 8, 9])
```

### End of stream
```python
stream = Stream(["a", "b", "c"]).on_end(lambda: print("Finished"))
char = stream.next().get()
if char == "a":
    stream.end()
```

## Examples

A given data structure like:
```python
data = {
   "ranges": [
      timedelta(days=3),
   ]
}
```

Without tinystream:
```python
if "ranges" in data:
    range_data: timedelta
    for range_data in filter(lambda x: isinstance(x, timedelta), data["ranges"]):
        pass
```

With tinystream:
```python
for range_data in Opt(data).map_key("ranges").stream().filter_type(timedelta):
    pass
```

## Comparison with other libraries

There are a couple of other implementation to fulfill similar requirements.

- https://github.com/vxgmichel/aiostream (most professional)
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
