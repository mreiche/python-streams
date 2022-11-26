from dataclasses import dataclass
from typing import List

from src.streams import Stream


def fibonacci():
    a = 1
    b = 1
    while True:
        yield b
        a, b = b, a + b


@dataclass
class Node:
    name: str
    parent: "Node" = None
    children: List["Node"] = None


def map_name(entity: Node):
    return entity.name


def flat_map_children(parent: Node):
    return parent.children


def compare_name(x: Node, y: Node):
    if x.name < y.name:
        return -1
    elif x.name > y.name:
        return 1
    else:
        return 0


def create_parents():
    parent_a = Node(name="Parent A")
    parent_b = Node(name="Parent B")
    child_a = Node(name="Child A")
    child_b1 = Node(name="Child B")
    child_b2 = Node(name="Child B2")

    parent_a.children = [child_a]
    child_a.parent = parent_a

    parent_b.children = [child_b1, child_b2]
    child_b1.parent = parent_b
    child_b2.parent = parent_b
    return parent_a, parent_b


def create_list():
    parent_a, parent_b = create_parents()
    data: List[Node] = [
        parent_a,
        parent_b
    ]
    return data


def create_numeric_list():
    return [1, 3, 5, 6, 2]


def create_string_list():
    return ["X", "Y", "A"]


def create_dict():
    parent_a, parent_b = create_parents()
    return {
        "parent_a": parent_a,
        "parent_b": parent_b
    }


def test_list_one():
    data = create_list()
    stream = Stream.of(data)

    assert stream.next().name == "Parent A"


def test_list_map():
    data = create_list()
    stream = Stream.of(data)
    for name in stream.map(map_name).each():
        assert name.startswith("Parent")


def test_list_map_type():
    parent_a, parent_b = create_parents()
    stream = Stream.of(parent_b.children)
    assert stream.map(lambda x: x.parent, Node).next().name == "Parent B"


def test_string_one():
    stream = Stream.of("Hallo Welt", str)
    assert stream.next() == "H"


def test_string_one_ends():
    stream = Stream.of("H", str)
    assert stream.next() == "H"
    assert stream.next() is None


def test_list_flatmap_count():
    stream = Stream.of(create_list())
    assert stream.flatmap(lambda x: x.children, Node).count() == 3


def test_list_filter_count():
    stream = Stream.of(create_list())
    assert stream.filter(lambda x: x.name.endswith("A")).count() == 1


def test_list_sort():
    stream = Stream.of(create_list())
    assert stream.sort(compare_name, reverse=True).next().name.endswith("B")


def test_list_reverse():
    stream = Stream.of(create_list())
    assert stream.reverse().next().name.endswith("B")


def test_list_peak():
    stream = Stream.of(create_list())

    def extend_name(x: Node):
        x.name += " Extended"

    assert stream.peek(extend_name).next().name.endswith("Extended")


def test_stream_dict():
    stream = Stream.of_dict(create_dict())

    for item in stream.each():
        assert isinstance(item[0], str)
        assert isinstance(item[1], Node)


def test_generator_one():
    stream = Stream.of(fibonacci())
    assert stream.next() == 1
    assert stream.next() == 2
    assert stream.next() == 3
    assert stream.next() == 5
    assert stream.next() == 8
    assert stream.next() == 13

    assert stream.map(lambda x: x - 10).next() == 11

def test_numeric_list_min():
    stream = Stream.of(create_numeric_list())
    assert stream.min() == 1


def test_numeric_list_max():
    stream = Stream.of(create_numeric_list())
    assert stream.max() == 6


def test_numeric_list_sum():
    stream = Stream.of(create_numeric_list())
    assert stream.sum() == 17


def test_numeric_list_limit():
    stream = Stream.of(create_numeric_list())
    assert stream.limit(2).sum() == 4


def test_string_list_min():
    stream = Stream.of(create_string_list())
    assert stream.min() == "A"


def test_string_list_max():
    stream = Stream.of(create_string_list())
    assert stream.max() == "Y"


def test_string_list_sum():
    stream = Stream.of(create_string_list())
    assert stream.map(str.lower).sum() == "xya"


def test_numeric_list_concat():
    stream = Stream.of(create_numeric_list())
    assert stream.concat(create_numeric_list()).sum() == 34


def test_of_many_numeric_list():
    stream = Stream.of_many(
        int,
        create_numeric_list(),
        create_numeric_list(),
        create_numeric_list()
        )
    assert stream.sum() == 51


def test_doc():
    stream = Stream.of([1, 2, 3, 4, 5])

    sum = stream \
        .map(lambda x: x + 1) \
        .filter(lambda x: x > 2) \
        .sorted(int, reverse=True) \
        .reverse() \
        .limit(2) \
        .concat([4]) \
        .sum()

    assert sum == 11
