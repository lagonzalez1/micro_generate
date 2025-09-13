# test_gemini_model.py
import types
import pytest

# ⬇️ CHANGE THIS to your actual module path, e.g.:
# import app.gemini_model as main
import Models.GeminModel as main


# ---------- Fakes ----------
class _FakeModels:
    def __init__(self, text=None, exc=None):
        self._text = text
        self._exc = exc

    def generate_content(self, model=None, contents=None):
        if self._exc:
            raise self._exc
        # mimic SDK return: object with `.text`
        return types.SimpleNamespace(text=self._text)


class _FakeClient:
    def __init__(self, text=None, exc=None):
        self.models = _FakeModels(text=text, exc=exc)


# ---------- Tests ----------
def test_success_flow(monkeypatch):
    monkeypatch.setattr(main, "client", _FakeClient(text="Hello Gemini!"))

    m = main.GeminiModel(prompt="Generate materials for addition")
    assert m.valid_response() is True
    assert m.get_generation() == "Hello Gemini!"
    assert m.get_text_length() == len("Hello Gemini!")

    # total_token: (len("HelloGemini!")+2)//4
    compressed_len = len("".join("Hello Gemini!".split()))
    assert m.total_token() == (compressed_len + 2) // 4


def test_empty_text(monkeypatch):
    monkeypatch.setattr(main, "client", _FakeClient(text=""))

    m = main.GeminiModel(prompt="empty please")
    assert m.valid_response() is True
    assert m.get_generation() == ""
    assert m.get_text_length() == 0
    assert m.total_token() == 0  # (0+2)//4 == 0


def test_whitespace_text(monkeypatch):
    text = "a b\tc \n d"
    monkeypatch.setattr(main, "client", _FakeClient(text=text))

    m = main.GeminiModel(prompt="spaces")
    assert m.valid_response() is True
    compressed = "".join(text.split())  # "abcd"
    assert m.total_token() == (len(compressed) + 2) // 4  # (4+2)//4 == 1


def test_exception_path(monkeypatch):
    # Simulate client throwing inside generate_content
    monkeypatch.setattr(main, "client", _FakeClient(exc=RuntimeError("boom")))

    m = main.GeminiModel(prompt="should fail")
    assert m.valid_response() is False
    assert m.response is None

    # Accessors should error when response is None
    with pytest.raises(AttributeError):
        _ = m.get_generation()
    with pytest.raises(AttributeError):
        _ = m.get_text_length()
    with pytest.raises(AttributeError):
        _ = m.total_token()