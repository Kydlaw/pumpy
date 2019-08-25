#  coding: utf-8

import pumpy.creds as creds
from unittest.mock import patch
from pytest_mock import mocker


def test_generate_apil(mocker):
    mocker.patch("tweepy.AppAuthHandler")
    api1 = creds.AuthApi(mode="stream", token="fdsqgfgsdg", token_secret="bhgfdhgfdhdf")
    assert isinstance(api1, creds.AuthApi)
