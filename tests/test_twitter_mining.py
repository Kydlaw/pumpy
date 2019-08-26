from pumpy.twitter_mining import Miner
import pytest
from pytest_mock import mocker
import path


@pytest.fixture
def minerg():
    return Miner("getter")


@pytest.fixture
def miners():
    return Miner("stream")


def test_mode(minerg, miners):
    assert minerg.mode == "getter"
    assert miners.mode == "stream"


def test_from_file_exist(minerg, miners):
    with pytest.raises(FileNotFoundError):
        miners.from_file("../data/CrisisLexT26/Colorado_2016_ids.csv", 1)


def test_from_file_getter_only(mocker, miners):
    mocker.patch("path.Path.exists")
    with pytest.raises(ValueError):
        miners.from_file(path, 1)


def test_from_file_output(mocker, minerg):
    mocker.patch("path.Path.exists")
    result = minerg.from_file("this/is/a/path.txt", 1)
    assert result.input_file == "this/is/a/path.txt"
    assert result.index_ids == 1
