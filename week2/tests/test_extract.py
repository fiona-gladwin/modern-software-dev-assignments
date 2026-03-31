from ..app.services import extract as extract_service
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_with_bullet_list_input(monkeypatch):
    class DummyMessage:
        content = (
            '{"action_items":['
            '"Set up database",'
            '"implement API extract endpoint",'
            '"Write tests"'
            "]}"
        )

    class DummyResponse:
        message = DummyMessage()

    def fake_chat(**kwargs):
        assert kwargs["model"] == "llama3.1:8b"
        return DummyResponse()

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items_llm(text)
    assert items == [
        "Set up database",
        "implement API extract endpoint",
        "Write tests",
    ]


def test_extract_action_items_llm_with_keyword_prefixed_lines(monkeypatch):
    class DummyMessage:
        content = (
            '{"action_items":['
            '"Update design doc",'
            '"Verify deployment",'
            '"Create onboarding checklist"'
            "]}"
        )

    class DummyResponse:
        message = DummyMessage()

    def fake_chat(**kwargs):
        return DummyResponse()

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    text = """
    TODO: update design doc
    Action: verify deployment
    Next: create onboarding checklist
    """.strip()

    items = extract_action_items_llm(text)
    assert items == [
        "Update design doc",
        "Verify deployment",
        "Create onboarding checklist",
    ]


def test_extract_action_items_llm_with_empty_input():
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   \n\t") == []
