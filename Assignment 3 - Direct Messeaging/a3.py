# a3.py
"""Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python."""

# Replace the following placeholders with your information.

# Joohyung Oh
# joohyuo@uci.edu
# 70426210

import time
from pathlib import Path
from Profile import Profile
from ds_messenger import DirectMessenger as DM
import tkinter as tk
from tkinter import ttk, simpledialog


class Body(tk.Frame):
    """Body class that contains the main content area of the application."""
    def __init__(self, root, recipient_selected_callback=None):
        super().__init__(root)
        self.root = root
        self._contacts = []
        self._select_callback = recipient_selected_callback
        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the Body instance
        self._draw()

    def node_select(self, _event=None):
        """Handle selection of a contact in the Treeview."""
        sel = self.posts_tree.selection()
        if not sel:
            return
        index = int(sel[0])
        entry = self._contacts[index]
        if self._select_callback:
            self._select_callback(entry)

    def insert_contact(self, contact: str):
        """Insert a contact into the contact list and update the Treeview."""
        if contact not in self._contacts:
            self._contacts.append(contact)
            idx = len(self._contacts) - 1
            self._insert_contact_tree(idx, contact)

    def _insert_contact_tree(self, idx, contact: str):
        entry = (contact[:24] + "...") if len(contact) > 25 else contact
        self.posts_tree.insert('', 'end', iid=str(idx), text=entry)

    def insert_user_message(self, message: str):
        """append at end and right-justify via tag."""
        self.entry_editor.insert(tk.END, message + '\n', 'entry-right')
        self.entry_editor.see(tk.END)

    def insert_contact_message(self, message: str):
        """append at end and left-justify via tag."""
        self.entry_editor.insert(tk.END, message + '\n', 'entry-left')
        self.entry_editor.see(tk.END)

    def get_text_entry(self) -> str:
        """Get the text from the message editor."""
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text: str):
        """Set the text in the message editor."""
        self.message_editor.delete('1.0', tk.END)
        self.message_editor.insert('1.0', text)

    def clear_messages(self):
        """Clear the message entry area."""
        self.entry_editor.delete('1.0', tk.END)

    def _draw(self):
        posts_frame = tk.Frame(self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.posts_tree = ttk.Treeview(posts_frame, show='tree')
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(self, bg="")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        editor_frame = tk.Frame(entry_frame, bg="")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        scroll_frame = tk.Frame(entry_frame, bg="", width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

        message_frame = tk.Frame(self, bg="")
        message_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=False)

        self.message_editor = tk.Text(message_frame, height=5)
        self.message_editor.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self.entry_editor = tk.Text(editor_frame)
        self.entry_editor.tag_configure('entry-right', justify='right')
        self.entry_editor.tag_configure('entry-left', justify='left')
        self.entry_editor.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        entry_editor_scrollbar = tk.Scrollbar(scroll_frame, command=self.entry_editor.yview)
        self.entry_editor['yscrollcommand'] = entry_editor_scrollbar.set
        entry_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False)


class Footer(tk.Frame):
    """Footer class that contains the send button and status label."""
    def __init__(self, root, send_callback=None):
        super().__init__(root)
        self._send_callback = send_callback
        self._draw()

    def send_click(self):
        """Handle the click event for the send button."""
        if self._send_callback:
            self._send_callback()

    def _draw(self):
        send_button = tk.Button(self, text="Send", width=20, command=self.send_click)
        # You must implement this.
        # Here you must configure the button to bind its click to
        # the send_click() function.
        send_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)
        self.footer_label = tk.Label(self, text="Ready.")
        self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)


class NewContactDialog(tk.simpledialog.Dialog):
    """Dialog for configuring the Direct Messenger server and user credentials."""
    def __init__(self, root, title=None, user=None, pwd=None, server=None):
        self.root = root
        self.server = server
        self.user = user
        self.pwd = pwd
        super().__init__(root, title)

    def body(self, frame):
        self.server_label = tk.Label(frame, width=30, text="DS Server Address")
        self.server_label.pack()
        self.server_entry = tk.Entry(frame, width=30)
        self.server_entry.insert(tk.END, self.server)
        self.server_entry.pack()

        self.username_label = tk.Label(frame, width=30, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.insert(tk.END, self.user)
        self.username_entry.pack()

        # You need to implement also the region for the user to enter
        # the Password. The code is similar to the Username you see above
        # but you will want to add self.password_entry['show'] = '*'
        # such that when the user types, the only thing that appears are
        # * symbols.
        #self.password...
        self.password_label = tk.Label(frame, width=30, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(frame, width=30)
        self.password_entry.insert(tk.END, self.pwd)
        self.password_entry['show'] = '*'
        self.password_entry.pack()

    def apply(self):
        self.user = self.username_entry.get()
        self.pwd = self.password_entry.get()
        self.server = self.server_entry.get()


class MainApp(tk.Frame):
    """Main application class that initializes the GUI and handles user interactions."""
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.username = ''
        self.password = ''
        self.server = ''
        self.recipient = ''
        self.direct_messenger = None
        self.profile = None
        self.profile_path = None
        # You must implement this! You must configure and
        # instantiate your DirectMessenger instance after this line.
        #self.direct_messenger = ... continue!

        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the root frame
        self._draw()

    def send_message(self):
        """Send the message in the text entry to the selected contact."""
        msg = self.body.get_text_entry()
        if not msg:
            self.footer.footer_label.config(text="Type a message first.")
            return
        if not self.recipient:
            self.footer.footer_label.config(text="Select a contact on the left.")
            return
        ok = self.publish(msg)
        if ok:
            self.body.set_text_entry('')
            # make sure the peer is saved as a contact
            if self.profile:
                self.profile.add_contact(self.recipient)
                self.profile.log_dm(self.recipient, 'out', msg, time.time())
                self.profile.save_profile(str(self.profile_path))
            self.refresh_current_conversation()

    def add_contact(self):
        """Prompt the user for a new contact name and add it to the contact list."""
        # Hint: check how to use tk.simpledialog.askstring to retrieve
        # the name of the new contact, and then use one of the body
        # methods to add the contact to your contact list
        name = simpledialog.askstring('Add Contact', "Enter contact username:", parent=self.root)
        if name:
            self.body.insert_contact(name)
            if self.profile:
                self.profile.add_contact(name)
                self.profile.save_profile(str(self.profile_path))

    def recipient_selected(self, recipient):
        """Callback for when a contact is selected in the Body."""
        self.recipient = recipient
        self.refresh_current_conversation()

    def configure_server(self):
        """Configure the server connection and user credentials."""
        ud = NewContactDialog(
            self.root, "Configure Account", self.username, self.password, self.server
        )
        self.username, self.password, self.server = ud.user, ud.pwd, ud.server

        # Prepare a per-user DSU file (profiles/alice.dsu)
        Path("profiles").mkdir(exist_ok=True)
        self.profile_path = Path("profiles") / f"{self.username}.dsu"

        # Create file first time so save_profile() won’t raise
        if not self.profile_path.exists():
            self.profile_path.touch()

        # Load or create profile
        self.profile = Profile(self.server, self.username, self.password)
        try:
            self.profile.load_profile(str(self.profile_path))
        except Exception:
            # first run, just save a blank profile
            self.profile.save_profile(str(self.profile_path))

        # hydrate UI from local profile
        for c in self.profile.contacts:
            self.body.insert_contact(c)
        self.refresh_current_conversation()

        # (then try to connect; if it fails, you still have local data)
        try:
            self.direct_messenger = DM(self.server, self.username, self.password)
            self.footer.footer_label.config(text="Connected.")

            # Call retrieve_all() exactly once at a good time:
            if not self.profile.direct_messages:
                dms = self.direct_messenger.retrieve_all()
                self._merge_server_messages(dms)
                # refresh contacts and the currently selected conversation
                for c in self.profile.contacts:
                    self.body.insert_contact(c)
                self.refresh_current_conversation()

        except Exception as e:
            self.direct_messenger = None
            self.footer.footer_label.config(text=f"Offline mode: {e}")

        # You must implement this!
        # You must configure and instantiate your
        # DirectMessenger instance after this line.

    def publish(self, message: str) -> bool:
        """Send a message to the currently selected contact."""
        if not self.direct_messenger:
            self.footer.footer_label.config(text="Not connected. Configure server first.")
            return False

        result = self.direct_messenger.send(message, self.recipient)
        if isinstance(result, tuple):
            ok, msg_text = result
        else:
            ok, msg_text = bool(result), ""


        if ok:
            self.footer.footer_label.config(text="Sent.")
        else:
            self.footer.footer_label.config(text=f"Send failed: {msg_text}")
        return ok

    def refresh_current_conversation(self):
        """Render only the messages for the currently selected contact."""
        self.body.clear_messages()
        if not self.recipient:
            return

        # Use locally persisted messages (works online & offline)
        msgs = self.profile.direct_messages if self.profile else []
        convo = [m for m in msgs if m['peer'] == self.recipient]
        convo.sort(key=lambda m: float(m['timestamp']))

        for m in convo:
            if m['direction'] == 'in':
                self.body.insert_contact_message(m['message'])
            else:
                self.body.insert_user_message(m['message'])

    def _merge_server_messages(self, dm_list):
        """Merge DirectMessage objects from server into the local profile without duplicates."""
        if not self.profile:
            return
        seen = {
            (m['peer'], m['direction'], m['message'], str(m['timestamp']))
            for m in self.profile.direct_messages
        }

        changed = False
        for dm in dm_list:
            if dm.sender:
                peer, direction = dm.sender, 'in'
            else:
                peer, direction = dm.recipient, 'out'
            key = (peer, direction, dm.message, str(dm.timestamp))
            if key not in seen:
                self.profile.add_contact(peer)
                self.profile.log_dm(peer, direction, dm.message, float(dm.timestamp or time.time()))
                seen.add(key)
                changed = True

        if changed:
            self.profile.save_profile(str(self.profile_path))


    def check_new(self):
        """Check for new messages from the server and update the UI."""
        try:
            if self.direct_messenger:
                new_msgs = self.direct_messenger.retrieve_new()
                for dm in new_msgs:
                    if self.profile:
                        self.profile.add_contact(dm.sender)
                        self.profile.log_dm(
                            dm.sender, 'in', dm.message, float(dm.timestamp or time.time())
                        )
                        self.profile.save_profile(str(self.profile_path))
                    if any(dm.sender == self.recipient for dm in new_msgs):
                        self.refresh_current_conversation()
                    # Ensure the sender appears in contacts
                    if dm.sender:
                        self.body.insert_contact(dm.sender)
                        # Only show messages from the selected contact in this window:
                        if self.recipient == dm.sender:
                            self.body.insert_contact_message(dm.message)
            # schedule next poll
            self.root.after(2000, self.check_new)
        except (OSError, RuntimeError) as e:
            self.footer.footer_label.config(text=f"Poll error: {e}")

    def _draw(self):
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New')
        menu_file.add_command(label='Open...')
        menu_file.add_command(label='Close')

        settings_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=settings_file, label='Settings')
        settings_file.add_command(label='Add Contact', command=self.add_contact)
        settings_file.add_command(label='Configure DS Server', command=self.configure_server)

        # The Body and Footer classes must be initialized and
        # packed into the root window.
        self.body = Body(self.root, recipient_selected_callback=self.recipient_selected)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root, send_callback=self.send_message)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)

if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Messenger")

    # This is just an arbitrary starting point. You can change the value
    # around to see how the starting size of the window changes.
    main.geometry("720x480")

    # adding this option removes some legacy behavior with menus that
    # some modern OSes don't support. If you're curious, feel free to comment
    # out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the
    # widgets used in the program. All of the classes that we use,
    # subclass Tk.Frame, since our root frame is main, we initialize
    # the class with it.
    app = MainApp(main)

    # When update is called, we finalize the states of all widgets that
    # have been configured within the root frame. Here, update ensures that
    # we get an accurate width and height reading based on the types of widgets
    # we have used. minsize prevents the root window from resizing too small.
    # Feel free to comment it out and see how the resizing
    # behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    after_id = main.after(2000, app.check_new)
    print(after_id)
    # And finally, start up the event loop for the program (you can find
    # more on this in lectures of week 9 and 10).
    main.mainloop()
