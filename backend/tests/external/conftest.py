import os

import pytest


@pytest.fixture(scope="session")
def environ():
    env = os.getenv("ENVIRON", None)
    assert env is not None, "ENVIRON is not set"
    return env


@pytest.fixture(scope="session")
def smear_host(environ):
    smear_host = os.getenv("SMEAR_HOST", None)

    if smear_host is None and environ:
        smear_host = {
            "local": "http://localhost:8000",
            "prod": "https://playsmeartest.herokuapp.com",
        }[environ]

    assert smear_host, f"SMEAR_HOST envvar is not set, and could not find host matching environ: {environ}"
    return smear_host


@pytest.fixture(scope="session")
def state():
    """Sets up a state dict that tests can use to pass data to each other.

    Simply add 'state' to your test function signature, and then access and set dict keys
    appropriately. For example, tests that create objects like organizations should set those
    IDs into this state dict so that subsequent tests can retrieve/modify the same object.
    """
    return {}
