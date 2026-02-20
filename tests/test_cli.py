import subprocess
import sys

import pytest


def test_cli_pipe():
    result = subprocess.run(
        [sys.executable, "-m", "half_json.cli", "--single"],
        input='{"a":',
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{"a":null}'


@pytest.mark.skipif(sys.version_info >= (3, 13), reason="Python 3.13+ accepts trailing commas in JSON")
def test_cli_multiline():
    result = subprocess.run(
        [sys.executable, "-m", "half_json.cli"],
        input='{"a":1,\n[1\n',
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    lines = result.stdout.strip().split("\n")
    assert lines[0] == '{"a":1}'
    assert lines[1] == '[1]'
