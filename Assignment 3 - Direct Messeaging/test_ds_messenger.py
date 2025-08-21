"""Minimal tests for DirectMessenger (no network).
Aim: cover success/error paths and key branches with few tests.
"""
# pylint: disable=protected-access

import io
import json
import socket
import pytest

from ds_messenger import DirectMessenger, DirectMessage


class DummyFile(io.StringIO):
    """StringIO that flushes on write like a real file."""
    def write(self, data):
        super().write(data)
        self.flush()

def test_send_when_not_authenticated_returns_false():
    """Test case."""
    dm = DirectMessenger()
    ok = dm.send("hi", "bob")
    assert ok is False
    assert "Not authenticated" in dm.last_message


def test_send_success_and_json_shape():
    """Test case."""
    dm = DirectMessenger()
    dm.token = "tok"
    dm.send_file = DummyFile()
    dm.recv_file = DummyFile(json.dumps({"response": {"type": "ok", "message": "ok"}}) + "\n")
    assert dm.send("m", "bob") is True
    raw = dm.send_file.getvalue().strip().splitlines()[-1]
    payload = json.loads(raw)
    assert payload["token"] == "tok"
    b = payload["directmessage"]
    assert b["entry"] == "m" and b["recipient"] == "bob" and isinstance(b["timestamp"], str)


def test_fetch_ok_parses_sender_and_recipient():
    """Test case."""
    response = {"response": {"type": "ok", "messages": [
        {"message": "A", "timestamp": "1", "from": "alice"},
        {"message": "B", "timestamp": "2", "recipient": "bob"},
    ]}}
    dm = DirectMessenger()
    dm.token = "tok"
    dm.send_file = DummyFile()
    dm.recv_file = DummyFile(json.dumps(response) + "\n")
    out = dm._fetch("all")
    assert isinstance(out[0], DirectMessage) and out[0].sender == "alice" and out[0].recipient is None
    assert out[1].recipient == "bob" and out[1].sender is None


def test_fetch_error_sets_last_message():
    """Test case."""
    dm = DirectMessenger()
    dm.token = "tok"
    dm.send_file = DummyFile()
    dm.recv_file = DummyFile(json.dumps({"response": {"type": "error", "message": "bad"}}) + "\n")
    out = dm._fetch("all")
    assert not out and dm.last_message == "bad"


def test_fetch_invalid_json_sets_last_message():
    """Test case."""
    dm = DirectMessenger()
    dm.token = "tok"
    dm.send_file = DummyFile()
    dm.recv_file = DummyFile("{not json}\n")
    out = dm._fetch("all")
    assert not out and "Failed to decode" in dm.last_message


def test_parse_addr_variants():
    """Test case."""
    dm = DirectMessenger()
    assert dm._parse_addr("h:4000") == ("h", 4000)
    assert dm._parse_addr("127.0.0.1") == ("127.0.0.1", 3001)
    assert dm._parse_addr("h:notaport") == ("h:notaport", 3001)


def test_connect_success_and_error(monkeypatch):
    """Test case: ok then error paths."""
    ok_resp = json.dumps({"response": {"type": "ok", "message": "hi", "token": "T"}}) + "\n"
    err_resp = json.dumps({"response": {"type": "error", "message": "no"}}) + "\n"

    class _SockOK:
        def __init__(self):
            self._r = DummyFile(ok_resp)
            self._w = DummyFile()
        def connect(self, _):
            '''Simulate a successful connection.'''
            return None
        def makefile(self, m):
            '''Return the appropriate file based on mode m.'''
            return self._r if "r" in m else self._w
        def close(self):
            '''Simulate a connection close.'''
            return None

    class _SockERR:
        def __init__(self):
            self._r = DummyFile(err_resp)
            self._w = DummyFile()
        def connect(self, _):
            '''Simulate a connection error.'''
            return None
        def makefile(self, m):
            '''Return the appropriate file based on mode m.'''
            return self._r if "r" in m else self._w
        def close(self):
            '''Simulate a connection error.'''
            return None

    # success
    monkeypatch.setattr(socket, "socket", lambda *a, **k: _SockOK())
    dm = DirectMessenger("h:1", "u", "p")
    dm.connect()
    assert dm.token == "T" and dm.last_message == "hi"

    # error
    monkeypatch.setattr(socket, "socket", lambda *a, **k: _SockERR())
    dm2 = DirectMessenger("h:1", "u", "bad")
    with pytest.raises(RuntimeError):
        dm2.connect()
