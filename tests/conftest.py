import pytest
from agent_failure_taxonomy.fixtures import generate
from agent_failure_taxonomy.cli import read_input

@pytest.fixture
def fixture_dir(tmp_path):
    generate(tmp_path / "input")
    return tmp_path / "input"

@pytest.fixture
def records(fixture_dir):
    return read_input(fixture_dir)
