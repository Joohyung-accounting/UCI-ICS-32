# ds_messenger.py

"""Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python."""

# Replace the following placeholders with your information.

# Joohyung Oh
# joohyuo@uci.edu
# 70426210

import socket
import json
import time
from ds_protocol import extract_json


class DirectMessage:
    """DirectMessage class representing a direct message."""
    def __init__(self):
        self.recipient = None
        self.message = None
        self.sender = None
        self.timestamp = None


class DirectMessenger:
    """DirectMessenger class for sending and receiving direct messages."""
    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver
        self.username = username
        self.password = password

        self.client = None
        self.send_file = None
        self.recv_file = None

        self.token = None
        self.last_message = None

        # Establish connection & authenticate once if we have creds
        if all([self.dsuserver, self.username, self.password]):
            self.connect()

    # -------------------- connection/auth -------------------- #

    def _parse_addr(self, addr: str) -> tuple[str, int]:
        """Return (host, port) from 'host' or 'host:port'."""
        if addr and ":" in addr:
            host, port = addr.split(":", 1)
            try:
                return host, int(port)
            except ValueError:
                pass
        return addr, 3001  # default port per spec/autograder

    def connect(self) -> None:
        """Connect to the Direct Messenger server and authenticate."""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = self._parse_addr(self.dsuserver)
        self.client.connect((host, port))
        self.send_file = self.client.makefile("w")
        self.recv_file = self.client.makefile("r")

        auth_request = json.dumps({
            "authenticate": {"username": self.username, "password": self.password}
        })
        self.send_file.write(auth_request + "\n")
        self.send_file.flush()

        response = self.recv_file.readline().strip()
        server_response = extract_json(response)
        self.last_message = server_response.message
        if server_response.type == "ok":
            self.token = server_response.token
        else:
            raise Exception("Authentication failed: " + str(server_response.message))

    # --------------------- public API ------------------------ #

    def send(self, message: str, recipient: str) -> bool:
        """Return True if server ack'd the direct message; else False."""
        if not self.token:
            self.last_message = "Not authenticated"
            return False

        timestamp = str(time.time())
        dir_message = json.dumps({
            "token": self.token,
            "directmessage": {
                "entry": message,
                "recipient": recipient,
                "timestamp": timestamp
            }
        })
        self.send_file.write(dir_message + "\n")
        self.send_file.flush()

        response = self.recv_file.readline().strip()
        server_response = extract_json(response)
        self.last_message = server_response.message
        return server_response.type == "ok"

    def retrieve_new(self) -> list:
        """Return a list of unread DirectMessages."""
        return self._fetch("unread")

    def retrieve_all(self) -> list:
        """Return a list of all DirectMessages."""
        return self._fetch("all")

    # --------------------- helpers --------------------------- #

    def _fetch(self, mode: str) -> list:
        """Return a list of DirectMessage for 'unread' or 'all'."""
        if not self.token:
            self.last_message = "Not authenticated"
            return []

        fetch_msg = json.dumps({"token": self.token, "fetch": mode})
        self.send_file.write(fetch_msg + "\n")
        self.send_file.flush()

        line = self.recv_file.readline().strip()
        try:
            obj = json.loads(line)
            resp = obj.get("response", {})
            if resp.get("type") != "ok":
                self.last_message = resp.get("message")
                return []

            messages = resp.get("messages", [])
            result = []
            for m in messages:
                dm = DirectMessage()
                dm.message = m.get("message")
                dm.timestamp = m.get("timestamp")
                if "from" in m:
                    dm.sender = m.get("from")
                if "recipient" in m:
                    dm.recipient = m.get("recipient")
                result.append(dm)
            return result
        except (json.JSONDecodeError, AttributeError, TypeError):
            self.last_message = "Failed to decode messages."
            return []
