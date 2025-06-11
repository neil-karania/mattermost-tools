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


def test_notify_channel():
    from mattermost_notify.api import notify_channel, wakeup

    wakeup(config=config)
    notify_channel("Hello, World!", channel_name=test_channel_name)


def test_notify_user():
    from mattermost_notify.api import notify_user, wakeup

    wakeup(config=config)
    notify_user("Hello, World!", user_name=test_user_name)


def test_notify_with_standard_channel():
    from mattermost_notify.api import notify_channel, wakeup

    wakeup(config=config, always_send_to_channel=test_channel_name)
    notify_channel("Hello, World! once")
    notify_channel("Hello, World! twice")


def test_notify_with_standard_user():
    from mattermost_notify.api import notify_user, wakeup

    wakeup(config=config, always_send_to_user=test_user_name)
    notify_user("Hello, World! once")
    notify_user("Hello, World! twice")


def test_notify_with_image_upload_to_user():
    from mattermost_notify.api import notify_user, wakeup

    wakeup(config=config, always_send_to_user=test_user_name)
    notify_user(
        "Hello, World! once", files=["tests/test_api.py", "tests/test_kitty.jpg"]
    )
    notify_user(
        "Hello, World! twice", files=["tests/test_api.py", "tests/test_kitty.jpg"]
    )


def test_send_markdown_to_channel():
    from mattermost_notify.api import notify_channel, wakeup

    wakeup(config=config, always_send_to_channel=test_channel_name)
    msg = """

# This is a title

With a paragraph underneath

> then a quote here
"""
    notify_channel(msg)


def test_send_using_notify_toplevel():

    import mattermost_notify as notify

    notify.wakeup(config=config)
    notify.notify("Test with toplevel", user_name=test_user_name)


def test_send_using_notify_toplevel_with_standard_user():

    import mattermost_notify as notify

    notify.wakeup(config=config, always_send_to_user=test_user_name)
    notify.notify("Test with toplevel")


def test_send_update():
    import mattermost_notify as notify
    from time import sleep

    notify.wakeup(config=config)
    notify.notify_channel(
        "Hello, World! once", channel_name=test_channel_name, id="test"
    )
    sleep(3)
    notify.send_update("Hello, World! twice", id="test")


def test_send_update_with_toplevel_notify():
    import mattermost_notify as notify
    from time import sleep

    notify.wakeup(config=config)
    notify.notify(
        "Hello, World /toplevel ! once", channel_name=test_channel_name, id="test"
    )
    sleep(3)
    notify.notify("Hello, World /toplevel ! twice", id="test")


def test_export_and_import_hooks():

    import mattermost_notify as notify
    from time import sleep

    notify.wakeup(config=config)
    notify.notify_channel(
        "Hello, World! from api original", channel_name=test_channel_name, id="test"
    )
    notify.export_hook("test", "tests/test_hook.msg")

    sleep(3)

    # initialize new client
    notify.wakeup(config=config)
    notify.import_hook("tests/test_hook.msg")

    notify.send_update("Hello, World! from api updated", id="test")

    import os

    if os.path.exists("tests/test_hook.msg"):
        os.remove("tests/test_hook.msg")
