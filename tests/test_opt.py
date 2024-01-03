import pytest

from tinystream import Opt


def test_opt_absent():
    assert Opt(None).empty
    assert Opt(None).absent


def test_opt_value():
    assert Opt("Hallo").get() == "Hallo"


def test_opt_empty_default():
    assert Opt(None).get("Welt") == "Welt"


def test_opt_empty_default_callable():
    assert Opt(None).get(lambda: "Welt") == "Welt"


def test_opt_empty_raise():
    with pytest.raises(Exception) as e:
        Opt(None).get()

    assert "Cannot get value of empty Opt without default value" in e.value.args[0]


def test_opt_value_if_present():
    if_present = None

    def _present(given):
        nonlocal if_present
        if_present = given

    Opt("Hallo").if_present(_present)
    assert if_present == "Hallo"


def test_opt_empty_if_present():
    if_present = None

    def _present(given):
        nonlocal if_present
        if_present = given

    Opt(None).if_present(_present)
    assert if_present is None


def test_opt_value_if_absent_callable():
    assert Opt("Hallo").if_absent(lambda: "Empty").get() == "Hallo"


def test_opt_empty_if_empty_callable():
    assert Opt(None).if_absent(lambda: "Empty").get() == "Empty"


def test_opt_empty_if_empty_value():
    assert Opt(None).if_absent("Empty").get() == "Empty"
    assert Opt(None).if_empty("Empty").get() == "Empty"


def test_opt_value_map():
    assert Opt("Hallo").map(len).get() == 5


def test_opt_value_filter_is_empty():
    assert Opt(0).filter(lambda x: x > 0).absent


def test_opt_value_filter_not_empty():
    assert Opt(1).filter(lambda x: x > 0).present


def test_none_opt_filter():
    assert Opt(None).filter(lambda x: x is not None).absent


def test_none_opt_map():
    assert Opt(None).map(len).get(0) == 0


def test_filter_type():
    assert Opt("string").filter_type(int).absent


def test_type():
    assert Opt("0").type(int).get() == "0"


def test_filter_key_value():
    assert Opt({"name": "Hallo"}).filter_key("name").present


def test_filter_key_empty():
    assert Opt({"name": "Hallo"}).filter_key("inexistent").absent


def test_map_key_value():
    assert Opt({"name": "Hallo"}).map_key("name").get() == "Hallo"


def test_map_key_empty():
    assert Opt({"name": "Hallo"}).map_key("inexistent").absent


def test_map_keys():
    data = {
        "address": {
            "street": {
                "name": "Grove"
            }
        }
    }
    opt = Opt(data)
    assert opt.map_keys("address", "street", "name").get() == "Grove"
    assert opt.map_keys("address", "street", "number").absent
    assert opt.map_keys("person", "name", "first").absent

    empty_opt = opt.map_keys("inexistent")
    assert empty_opt.filter_key("inexistent") == empty_opt
    assert empty_opt.filter(lambda x: x is not None) == empty_opt


def test_stream():
    data = {
        "list": [1, 2, 3]
    }

    opt = Opt(data)
    assert opt.map_key("list").stream().sum().get() == 6
    assert opt.map_key("inexistent").stream().sum().absent
