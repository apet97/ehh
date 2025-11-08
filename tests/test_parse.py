
from app.actions import parse_human

def test_parse_basic():
    a = parse_human("slack.post_message channel=#general text=hi")
    assert a.integration == "slack"
    assert a.operation == "post_message"
    assert a.params["channel"] == "#general"
    assert a.params["text"] == "hi"
