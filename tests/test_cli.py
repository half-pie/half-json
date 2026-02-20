import subprocess
import sys


def test_cli_pipe():
    result = subprocess.run(
        [sys.executable, "-m", "half_json.cli", "--single"],
        input='{"a":',
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == '{"a":null}'


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
