[![Tests Status](https://github.com/mreiche/python-streams/actions/workflows/tests.yml/badge.svg)](https://github.com/mreiche/python-streams/actions/workflows/tests.yml)
[![Code Coverage Status](https://codecov.io/github/mreiche/python-streams/branch/main/graph/badge.svg)](https://app.codecov.io/github/mreiche/python-streams)
[![PyPI version](https://badge.fury.io/py/tinystream.svg)](https://badge.fury.io/py/tinystream)

# tinystream / python-streams

This is a simple and lightweight Streams API inspired by Java Streams with support for type hinting.

This package is released as `tinystream` at pypi.

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

Some aggregators like `sum()`, `max()` are `Opt`:

```python
assert Stream((1, 2, 3, 4, 5)).sum().get() == 15
```

## More features

### Type hinting

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

### Filter by key value
```python
items_with_name = Stream([child]).filter_key_value("name", "Child")
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

### Opt usage

Get next value as `Opt`:

```python
assert Stream((1, 2, 3, 4, 5)).next().present
```

Mapping:
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

## Examples

### Write better code with `Stream`

```python
data = {
   "ranges": [
      {"days": 3},
      {"weeks": 1},
   ]
}

# With tinystream Stream
for range_data in Opt(data).map_key("ranges").stream().map_kwargs(timedelta):
   pass

# Vanilly Python
if "ranges" in data:
   range_data: timedelta
   for range_data in map(lambda x: timedelta(**x), data["ranges"]):
      pass
```

### Write better code with `Opt`
```python
# tinystream Opt
var = Opt(my_dict).kmap("key").filter(not_empty).get("default")

# Vanilla Python
var = my_dict["key"] if "key" in my_dict and not_empty(my_dict["key"]) else "default"
```


## Comparison with other libraries

There are a couple of other implementation to fulfill similar requirements.

- https://github.com/vxgmichel/aiostream
- https://github.com/python-streamz/streamz
- https://pypi.org/project/fluentpy
- https://github.com/ramsteak/streams 
- https://github.com/alemazzo/Python-Java-Stream  (*outdated*)
- https://github.com/JaviOverflow/python-streams (*outdated*)
- https://github.com/9seconds/streams/ (*outdated*)
- https://github.com/tolsac/streampy (*outdated*)
- Apache Spark

## Run the tests

```shell
PYTHONPATH="." pytest --cov=tinystream -n 4 tests/
```

## References

- https://github.com/MichaelKim0407/tutorial-pip-package
- https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
