# Profile.py
"""Profile module for assignment 2 (ICS 32)."""
# ICS 32
# Assignment #2: Journal
#
# Author: Mark S. Baldwin, modified by Alberto Krone-Martins
#
# v0.1.9

# You should review this code to identify what features you need to support
# in your program for assignment 2.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THE JSON SERIALIZATION ASPECTS OF THIS CODE
# RIGHT NOW, though can you certainly take a look at it if you are curious since we
# already covered a bit of the JSON format in class.
#
import json
import time
from pathlib import Path

class DsuFileError(Exception):
    """
DsuFileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to load or save Profile objects to file the system.
    """

class DsuProfileError(Exception):
    """
DsuProfileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to deserialize a dsu file to a Profile object.
    """


class Post(dict):
    """ 

    The Post class is responsible for working with individual user posts. It currently 
    supports two features: A timestamp property that is set upon instantiation and 
    when the entry object is set and an entry property that stores the post message.

    """
    def __init__(self, entry:str = None, timestamp:float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)

        # Subclass dict to expose Post properties for serialization
        # Don't worry about this!
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)

    def set_entry(self, entry: str) -> None:
        """Set the entry of the post and update the timestamp."""
        self._entry = entry
        dict.__setitem__(self, 'entry', entry)

        # If timestamp has not been set, generate a new from time module
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self) -> str:
        """Return the entry of the post."""
        return self._entry

    def set_time(self, time: float) -> None:
        """Set the timestamp of the post."""
        self._timestamp = time
        dict.__setitem__(self, 'timestamp', time)

    def get_time(self) -> float:
        """Return the timestamp of the post."""
        return self._timestamp

    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)

class Profile:
    """
    The Profile class exposes the properties required to join an ICS 32 DSU server. You 
    will need to use this class to manage the information provided by each new user 
    created within your program for a2. Pay close attention to the properties and 
    functions in this class as you will need to make use of each of them in your program.

    When creating your program you will need to collect user input for the properties 
    exposed by this class. A Profile class should ensure that a username and password 
    are set, but contains no conventions to do so. You should make sure that your code 
    verifies that required properties are set.

    """

    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver # REQUIRED
        self.username = username # REQUIRED
        self.password = password # REQUIRED
        self.bio = ''            # OPTIONAL
        self._posts = []         # OPTIONAL
        self.contacts = []
        self.direct_messages = []

    def add_post(self, post: Post) -> None:
        """Add a Post object to the profile's posts list."""
        self._posts.append(post)


    def del_post(self, index: int) -> bool:
        """
        del_post accepts an index as parameter and attempts to delete the Post object at
        that index. If the index is valid, the Post object is deleted and True is returned.
        If the index is invalid, the method returns False.
        """
        try:
            del self._posts[index]
            return True
        except IndexError:
            return False

    def get_posts(self) -> list[Post]:
        """Return the list of posts."""
        return self._posts

    def save_profile(self, path: str) -> None:
        """Save the current profile to a DSU file."""
        p = Path(path)

        if p.exists() and p.suffix == '.dsu':
            try:
                with open(p, 'w', encoding="utf-8") as f:
                    self._posts = [post.__dict__ for post in self._posts]
                    json.dump(self.__dict__, f)
            except Exception as ex:
                raise DsuFileError("Error while attempting to process the DSU file.", ex) from ex
        else:
            raise DsuFileError("Invalid DSU file path or type")

    def load_profile(self, path: str) -> None:
        """Load a profile from a DSU file."""
        p = Path(path)

        if p.exists() and p.suffix == '.dsu':
            try:
                with open(p, 'r', encoding="utf-8") as f:
                    obj = json.load(f)
                    self.username = obj['username']
                    self.password = obj['password']
                    self.dsuserver = obj['dsuserver']
                    self.bio = obj['bio']
                    self.contacts = obj.get('contacts', [])
                    self.direct_messages = obj.get('direct_messages', [])
                    for post_obj in obj['_posts']:
                        post = Post(post_obj['entry'], post_obj['timestamp'])
                        self._posts.append(post)
            except Exception as ex:
                raise DsuProfileError(ex) from ex
        else:
            raise DsuFileError()

    def add_contact(self, name: str) -> None:
        """Add a contact to the profile's contact list."""
        if name not in self.contacts:
            self.contacts.append(name)

    def log_dm(self, peer: str, direction: str, message: str, timestamp: float) -> None:
        """Log a direct message interaction with a peer."""
        self.direct_messages.append(
            {"peer": peer, "direction": direction, "message": message, "timestamp": timestamp}
        )
 # type: ignore