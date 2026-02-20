import pytest

from half_json.core import JSONFixer


@pytest.fixture
def fixer():
    return JSONFixer()


@pytest.fixture
def js_fixer():
    return JSONFixer(js_style=True)
