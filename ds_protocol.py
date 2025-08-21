# ds_protocol.py

"""Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python."""

# Replace the following placeholders with your information.

# Joohyung Oh
# joohyuo@uci.edu
# 70426210

import json
from collections import namedtuple

# Create a namedtuple to hold the values we expect to retrieve from json messages.
ServerResponse = namedtuple("ServerResponse", ["type","message","token"])

def extract_json(json_msg:str) -> ServerResponse:
    '''
    Call the json.loads function on a json string and convert it to a DataTuple object
    '''
    try:
        json_obj = json.loads(json_msg)
        response = json_obj.get("response", {})
        return ServerResponse (
            response.get("type"),
            response.get("message"),
            response.get("token")
        )

    except json.JSONDecodeError:
        return ServerResponse("error", "Invalid JSON format", None)
