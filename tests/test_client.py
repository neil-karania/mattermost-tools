from dotenv import dotenv_values

env_vars = dotenv_values(".env")

config = dict(
    url=env_vars["URL"],
    team_name=env_vars["TEAM_NAME"],
    bot_name=env_vars["BOT_NAME"],
    token=env_vars["TOKEN"],
    ssl_verify=env_vars["SSL_VERIFY"],
)

test_channel_name = env_vars["TEST_CHANNEL_NAME"]
test_user_name = env_vars["TEST_USER_NAME"]
test_channel_id = env_vars["TEST_CHANNEL_ID"]
test_user_id = env_vars["TEST_USER_ID"]


def test_can_connect():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    assert client.test_connection(), "Connection failed"


def test_can_get_user_id():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    user_id = client._Notify__get_user_id("noahhk")
    assert user_id == test_user_id, "User ID is incorrect"


def test_can_get_channel_id():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    channel_id = client._Notify__get_channel_id(test_channel_name)
    assert channel_id == test_channel_id, "Channel ID is incorrect"


def test_can_send_to_channel():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    response = client.send_to_channel("Hello, World!", channel_name=test_channel_name)
    assert response


def test_can_send_to_user():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    response = client.send_to_user("Hello, World!", user_name=test_user_name)
    assert response


def test_can_send_to_default_channel():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    client.set_default_channel(test_channel_name)
    response = client.send_to_channel("Hello, World!")
    assert response


def test_can_send_text_file_to_channel():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    response = client.send_to_channel(
        "Hello, World!", channel_name=test_channel_name, files=["tests/test_client.py"]
    )
    assert response


def test_can_send_text_file_to_user():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    response = client.send_to_user(
        "Hello, World!", user_name=test_user_name, files=["tests/test_client.py"]
    )
    assert response


def test_can_send_image_file_to_channel():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    response = client.send_to_channel(
        "The Notify Bot can upload even files now!",
        channel_name=test_channel_name,
        files=["tests/test_kitty.jpg"],
    )
    assert response


def test_can_send_image_file_to_user():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    response = client.send_to_user(
        "The Notify Bot can upload even files now!",
        user_name=test_user_name,
        files=["tests/test_kitty.jpg"],
    )
    assert response


def test_can_update_message():
    from mattermost_notify.client import Notify

    client = Notify(**config)
    assert client.send_to_channel(
        "Hello, World! **", channel_name=test_channel_name, id="test_message"
    )
    from time import sleep

    sleep(4)
    assert client.send_update("Hello, World! Updated **", id="test_message")


def test_read_and_write_message_files():
    import mattermost_notify as notify

    client = notify.Notify(**config)
    client.set_default_channel(test_channel_name)

    client.send_to_channel("Hello, World!", id="test")
    assert client.message_in_cache("test")

    client.write_message_hook_to_file("test", "tests/test_message.msg")

    client2 = notify.Notify(**config)
    assert not client2.message_in_cache("test")

    client2.read_message_hook_from_file("tests/test_message.msg")
    assert client2.message_in_cache("test")

    from time import sleep

    sleep(2)
    client2.send_update("Hello, World! from another client", id="test")

    import os

    os.remove("tests/test_message.msg")
