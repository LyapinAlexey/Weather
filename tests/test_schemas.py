import pytest
from schemas import CityRequestSchema
from marshmallow import ValidationError

def test_valid_city():
    schema = CityRequestSchema()
    res = schema.load({"city": "Moskow"})
    assert res["city"] == "Moskow"
def test_city_min_length_boundary():
    schema = CityRequestSchema()
    res = schema.load({"city": "a"})
    assert res["city"] == "a"
def test_city_max_length_boundary():
    schema = CityRequestSchema()
    res = schema.load({"city": "a" * 100})
    assert res["city"] == "a" * 100

def test_missing_city_raises_error():
    schema  = CityRequestSchema()
    with pytest.raises(ValidationError):
        schema.load({})
def test_empty_city_raises_error():
    schema = CityRequestSchema()
    with pytest.raises(ValidationError):
        schema.load({"city": ""})
def test_city_too_long_raises_error():
    schema = CityRequestSchema()
    with pytest.raises(ValidationError):
        schema.load({"city": "a" * 101})