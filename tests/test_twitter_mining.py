from pumpy.twitter_mining import Miner
import pytest
from pytest_mock import mocker
from path import Path
import os


@pytest.fixture
def minerg():
    return Miner("getter")


@pytest.fixture
def miners():
    return Miner("stream")


def test_mode(minerg, miners):
    assert minerg.mode == "getter"
    assert miners.mode == "stream"


def test_from_file_getter_only(mocker, miners):
    mocker.patch("path.Path.exists")
    with pytest.raises(ValueError):
        miners.from_file("bonjour", 1)


def test_from_file_output(mocker, minerg):
    mocker.patch("path.Path.exists")
    result = minerg.from_file("this/is/a/path.txt", 1)
    assert result.input_file_path == Path("this/is/a/path.txt")
    assert result.index_ids == 1


def test_to_no_input_file_specified(minerg):
    with pytest.raises(ValueError):
        minerg.to("this/is/a/path.txt")


# def test_to_file_incrementation(tmp_path, miners):
#     d = tmp_path / "data/tweets"
#     d.mkdir()
#     miners.to(d)
#     assert d / "stream0.txt" == miners.output_file_path
#     miners.to(d)
#     assert d / "stream1.txt" == miners.output_file_path


def test_to_output(minerg, tmp_path):
    p = tmp_path / "data/tweets/"
    minerg.input_file_path = "data/CrisisLexT26/Colorado_wildfire/Colorado_ids.csv"
    minerg.to(p)
    assert minerg.output_file_path == Path(
        tmp_path / "data/tweets/Colorado_wildfire.json"
    )


def test_miner_from_file_to(mocker, minerg, tmp_path):
    mocker.patch("path.Path.exists")
    p = tmp_path / "data/tweets/"
    from_path = "data/CrisisLexT26/Colorado_wildfire/Colorado_ids.csv"
    minerg.from_file(from_path, 1).to(p)
    assert minerg.mode == "getter"
    assert minerg.input_file_path == from_path
    assert minerg.output_file_path == Path(
        tmp_path / "data/tweets/Colorado_wildfire.json"
    )


def test_search(miners):
    miners.search("twitter", "python", "banane")
    assert miners.keywords == ["twitter", "python", "banane"]
    miners.search([0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8])
    assert miners.locations == [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
    miners.search("bonjour", [0.11, 0.21, 0.31, 0.41])
    assert miners.keywords == ["twitter", "python", "banane", "bonjour"]
    assert miners.locations == [
        [0.1, 0.2, 0.3, 0.4],
        [0.5, 0.6, 0.7, 0.8],
        [0.11, 0.21, 0.31, 0.41],
    ]
    with pytest.raises(ValueError):
        miners.search([1, 2, 3])


def test_mine_output():
    pass


def test_new_file_name():
    pass
