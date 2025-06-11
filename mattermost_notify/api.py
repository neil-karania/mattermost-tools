from .client import Notify
from .config import get_config

__notify = None
"""
The default notify client
"""

__default_user = None
"""
The default user to send messages to
"""

__default_channel = None
"""
The default channel to send messages to
"""


def notify(
    message: str,
    user_name: str = None,
    channel_name: str = None,
    files: list = None,
    id: str = None,
):
    """
    Send a message to a user or channel (only one of the two can be specified in one call)

    Parameters
    ----------
    message : str
        The message to send
    user_name : str
        The name of the user to send the message to
    channel_name : str
        The name of the channel to send the message to
    files: list
        A list of file paths of files to upload  to the user-chat
    id: str
        An identifier for the message in case you want to update it later. If a message with the same
        id was sent before the message will be automatically updated.
    """
    if id is not None and __notify is not None and __notify.message_in_cache(id):
        send_update(message, id)
        return

    if not user_name and not channel_name:
        if __default_user:
            user_name = __default_user
        elif __default_channel:
            channel_name = __default_channel

    if user_name:
        notify_user(message, user_name=user_name, files=files, id=id)
    elif channel_name:
        notify_channel(message, channel_name=channel_name, files=files, id=id)
    else:
        raise ValueError("No user or channel specified")


def wakeup(
    always_send_to_user: str = None,
    always_send_to_channel: str = None,
    config: dict = None,
) -> Notify:
    """
    Create a Notify client

    Parameters
    ----------
    always_send_to_user : str
        The default user to send messages to
    always_send_to_channel : str
        The default channel to send messages to
    config : dict
        The configuration to use. By default a configuration file will be searched for. The dictionary must contain keys: "url", "team_name", and "token".
    """
    global __notify
    if config is None:
        config = get_config()
    client = Notify(
        url=config["url"], team_name=config["team_name"], bot_name=config["bot_name"], token=config["token"],
        ssl_verify=config["ssl_verify"]
    )
    __notify = client
    if always_send_to_user and always_send_to_channel:
        raise ValueError(
            "Default settings are mutually exclusive! Cannot send to both a user and a channel"
        )
    if always_send_to_user:
        global __default_user
        __default_user = always_send_to_user
    if always_send_to_channel:
        global __default_channel
        __default_channel = always_send_to_channel
    return client


def notify_channel(
    message: str, channel_name: str = None, files: list = None, id: str = None
):
    """
    Send a message to a channel

    Parameters
    ----------
    message : str
        The message to send
    channel_name : str
        The name of the channel to send the message to
    files: list
        A list of file paths of files to upload  to the channel
    id: str
        An identifier for the message in case you want to update it later.
    """
    if __notify is None:
        wakeup()
    if channel_name is None and __default_channel is None:
        raise ValueError("No channel specified and no default channel set")
    if channel_name is None:
        channel_name = __default_channel
    __notify.send_to_channel(message, channel_name=channel_name, files=files, id=id)


def notify_user(
    message: str, user_name: str = None, files: list = None, id: str = None
):
    """
    Send a message to a user

    Parameters
    ----------
    message : str
        The message to send
    user_name : str
        The name of the user to send the message to
    files: list
        A list of file paths of files to upload  to the user-chat
    id: str
        An identifier for the message in case you want to update it later.
    """
    if __notify is None:
        wakeup()
    if user_name is None and __default_user is None:
        raise ValueError("No user specified and no default user set")
    if user_name is None:
        user_name = __default_user
    __notify.send_to_user(message, user_name=user_name, files=files, id=id)


def send_update(message: str, id: str):
    """
    Update a message

    Parameters
    ----------
    message : str
        The new message
    id : str
        The identifier of the message to update that was sent when sending the message initially
    """
    if __notify is None:
        raise ValueError(
            "No Notify client set up that could be used to update a message"
        )
    __notify.send_update(message, id)


def export_hook(id: str, filename: str):
    """
    Export a message hook to a file

    Parameters
    ----------
    id : str
        The identifier of the message to export the hook of
    filename : str
        The filename to export the hook to
    """
    if __notify is None:
        raise ValueError(
            "No Notify client set up that could be used to export a message hook"
        )
    __notify.write_message_hook_to_file(id=id, filename=filename)


def import_hook(filename: str):
    """
    Import a message hook from a file

    Parameters
    ----------
    filename : str
        The filename to import the hook from
    """
    if __notify is None:
        raise ValueError(
            "No Notify client set up that could be used to import a message hook"
        )
    __notify.read_message_hook_from_file(filename)


__all__ = [
    "wakeup",
    "notify_channel",
    "notify_user",
    "notify",
    "send_update",
    "export_hook",
    "import_hook",
]
