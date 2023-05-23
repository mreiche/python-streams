import pytest

from tinystream import Opt


def test_opt_empty():
    assert Opt(None).empty


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


def test_opt_value_if_empty_callable():
    assert Opt("Hallo").if_empty(lambda: "Empty").get() == "Hallo"


def test_opt_empty_if_empty_callable():
    assert Opt(None).if_empty(lambda: "Empty").get() == "Empty"


def test_opt_empty_if_empty_value():
    assert Opt(None).if_empty("Empty").get() == "Empty"


def test_opt_value_map():
    assert Opt("Hallo").map(len).get() == 5


def test_opt_value_filter_is_empty():
    assert Opt(0).filter(lambda x: x > 0).empty is True


def test_opt_value_filter_not_empty():
    assert Opt(1).filter(lambda x: x > 0).empty is False


def test_opt_empty_filter():
    assert Opt(None).filter(lambda x: x is not None).empty is True


def test_filter_type():
    assert Opt("string").filter_type(int).empty is True


def test_type():
    assert Opt("0").type(int).get() == "0"
