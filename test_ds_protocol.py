"""Minimal tests for ds_protocol.extract_json and DM _fetch helpers."""
# pylint: disable=protected-access

import io
import json

from ds_messenger import DirectMessenger, DirectMessage
from ds_protocol import extract_json


class DummyFile(io.StringIO):
    """StringIO that flushes on write."""
    def write(self, data):
        super().write(data)
        self.flush()


def make_dm_with_response(response_dict):
    """Create a DirectMessenger wired to in-memory files."""
    dm = DirectMessenger("fake:3001", "user", "pw")
    dm.token = "tok"
    dm.send_file = DummyFile()
    dm.recv_file = DummyFile(json.dumps({"response": response_dict}) + "\n")
    return dm


def test_extract_json_ok_and_invalid_and_empty():
    """Test case."""
    ok = {"response": {"type": "ok", "message": "hi", "token": "t"}}
    r_ok = extract_json(json.dumps(ok))
    assert (r_ok.type, r_ok.message, r_ok.token) == ("ok", "hi", "t")

    r_empty = extract_json(json.dumps({"response": {}}))
    assert r_empty.type is None and r_empty.message is None and r_empty.token is None

    r_bad = extract_json("{bad}")
    assert r_bad.type == "error" and r_bad.token is None and r_bad.message


def test_fetch_success_minimal():
    """Test case."""
    messages = [{"message": "hello", "timestamp": "1", "from": "alice", "recipient": "bob"}]
    dm = make_dm_with_response({"type": "ok", "messages": messages})
    out = dm._fetch("all")
    m = out[0]
    assert isinstance(m, DirectMessage) and m.message == "hello" and m.sender == "alice" and m.recipient == "bob"
