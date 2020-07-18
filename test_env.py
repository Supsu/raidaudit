"""
Test module for environment

This module tests that all required environment variables
exist already or can be loaded from .env file. There is also
a test to check if values in those variables make sense.
"""

import os
from dotenv import load_dotenv


def test_env_available():
    """
    Test that env has all required keys.

    Data can exist in local .env file or already in env.
    """
    load_dotenv()

    print(os.environ)

    assert os.getenv("BNETID") is not None,\
        "Env doesn't have value for BNETID"
    assert os.getenv("BNETSECRET") is not None,\
        "Env doesn't have value for BNETSECRET"
    assert os.getenv("WCLKEY") is not None,\
        "Env doesn't have value for WCLKEY"
    assert os.getenv("WOWREGION") is not None,\
        "Env doesn't have value for WOWREGION"
    assert os.getenv("WOWGUILD") is not None,\
        "Env doesn't have value for WOWGUILD"
    assert os.getenv("WOWREALM") is not None,\
        "Env doesn't have value for WOWREALM"
    assert os.getenv("WOWNAMESPACE") is not None,\
        "Env doesn't have value for WOWNAMESPACE"
    assert os.getenv("WOWLOCALE") is not None,\
        "Env doesn't have value for WOWLOCALE"
    assert os.getenv("MONGOURL") is not None,\
        "Env doesn't have value for MONGOURL"
    assert os.getenv("MONGOPORT") is not None,\
        "Env doesn't have value for MONGOPORT"
    assert os.getenv("MONGOUSER") is not None,\
        "Env doesn't have value for MONGOUSER"
    assert os.getenv("MONGOPWD") is not None,\
        "Env doesn't have value for MONGOPWD"
    assert os.getenv("RAIDERRANK") is not None,\
        "Env doesn't have value for RAIDERRANK"
    assert os.getenv("FLASK_SECRET_KEY") is not None,\
        "Env doesn't have value for FLASK_SECRET_KEY"


def test_env_values():
    """
    Test env values have proper values.

    See that all values are within limitations.
    """

    # Battle.net values
    assert len(str(os.getenv("BNETID"))) == 32,\
        "BNETID should be 32 characters long, please check your env data"
    assert len(str(os.getenv("BNETSECRET"))) == 32,\
        "BNETSECRET should be 32 characters long, please check your env data"

    # Warcraftlogs key
    assert(len(str(os.getenv("WCLKEY")))) == 32,\
        "WCLKEY should be 32 characters long, please check your env data"

    # WoW data
    assert os.getenv("WOWREGION") in ["eu", "us"],\
        "For now other regions are not supported"
    assert int(os.getenv("RAIDERRANK")) < 10\
        and int(os.getenv("RAIDERRANK")) > -1,\
        "Your raider rank is either too big or too small"
