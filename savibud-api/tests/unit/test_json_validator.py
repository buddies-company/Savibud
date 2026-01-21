import pytest

from drivers.validators.json_validator import check_valid_dict_str


def test_valid_json_string():
    valid_json = '{"key": "value"}'
    assert check_valid_dict_str(valid_json) == valid_json


def test_invalid_json_string():
    invalid_json = '{"key": value}'  # value is not quoted
    with pytest.raises(ValueError, match="Invalid json format"):
        check_valid_dict_str(invalid_json)


def test_empty_string():
    empty_str = ""
    with pytest.raises(ValueError, match="Invalid json format"):
        check_valid_dict_str(empty_str)
