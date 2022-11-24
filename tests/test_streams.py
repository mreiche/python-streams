from dataclasses import dataclass
from typing import List

from src.streams import Stream

def fibonacci():
    a=1
    b=1
    for i in range(6):
        yield b
        a,b= b,a+b


@dataclass
class Node:
    name: str
    parent: "Node" = None
    children: List["Node"] = None


def map_name(entity: Node):
    return entity.name


def flat_map_children(parent: Node):
    return parent.children


def compare_name(x:Node, y:Node):
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


def create_dict():
    parent_a, parent_b = create_parents()
    return {
        "parent_a": parent_a,
        "parent_b": parent_b
    }


def test_list_one():
    data = create_list()
    stream = Stream.of(data)

    assert stream.one().name == "Parent A"


def test_list_map():
    data = create_list()
    stream = Stream.of(data)
    for name in stream.map(map_name).each():
        assert name.startswith("Parent")


def test_string_one():
    stream = Stream.of("Hallo Welt", str)
    assert stream.one() == "H"


def test_string_one_ends():
    stream = Stream.of("H", str)
    assert stream.one() == "H"
    assert stream.one() is None


def test_list_flatmap_count():
    stream = Stream.of(create_list())
    assert stream.flatmap(lambda x: x.children, Node).count() == 3


def test_list_filter_count():
    stream = Stream.of(create_list())
    assert stream.filter(lambda x: x.name.endswith("A")).count() == 1


def test_list_sort():
    stream = Stream.of(create_list())
    assert stream.sort(compare_name, reverse=True).one().name.endswith("B")


def test_list_reverse():
    stream = Stream.of(create_list())
    assert stream.reverse().one().name.endswith("B")


def test_list_peak():
    stream = Stream.of(create_list())

    def extend_name(x: Node):
        x.name += " Extended"

    assert stream.peak(extend_name).one().name.endswith("Extended")


def test_dict_one():
    stream = Stream.ofDict(create_dict())

    for item in stream.each():
        assert isinstance(item[0], str)
        assert isinstance(item[1], Node)


def test_generator_one():
    stream = Stream.of(fibonacci())
    assert stream.one() == 1
    assert stream.one() == 2
    assert stream.one() == 3
    assert stream.one() == 5
    assert stream.one() == 8
    assert stream.one() == 13
