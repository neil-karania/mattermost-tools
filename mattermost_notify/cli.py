"""
Command line interface for Mattermost Notify
"""

from argparse import ArgumentParser
from uuid import uuid4

parser = ArgumentParser(
    description="Send messages to Mattermost with Mattermost Notify!"
)
command = parser.add_subparsers(dest="command", help="The command to run.")
setup = command.add_parser("setup", help="Setup the Mattermost Notify configuration.")
send = command.add_parser("send", help="Send a message to a channel or user.")
update = command.add_parser(
    "update", help="Update a message sent by Mattermost Notify."
)
test = command.add_parser("test", help="Test the connection to the Mattermost server.")

setup.add_argument(
    "-i", "--interactive", help="Run in interactive mode.", action="store_true"
)
setup.add_argument("-u", "--url", help="The URL of the Mattermost server.")
setup.add_argument(
    "-n",
    "--team-name",
    help="The name of the team (the 'notify' bot needs to be a member!)",
)
setup.add_argument(
    "-b",
    "--bot-name",
    help="The name of the bot"
)
setup.add_argument(
    "-k",
    "--ssl-verify",
    help="enable/disable ssl verification",
    default=True,
    type=bool
)
setup.add_argument("-t", "--token", help="The access token for the 'notify' bot.")
setup.add_argument(
    "-o",
    "--output",
    help="The path where to write the .mattermost_notify file. By default Mattermost Notify will search in either $PWD or $HOME (defaults to $HOME)",
    default="$HOME",
)

send.add_argument("message", help="The message to send.")
send.add_argument(
    "-n",
    "--team-name",
    help="The name of the team (the 'notify' bot needs to be a member!)",
    default=None
)
dest = send.add_argument_group("Send to", "Send the message to a channel or user.")
dest.add_argument(
    "-c",
    "--channel",
    help="The name of the channel to send the message to. The 'notify' bot needs to have access to or be added to the channel!",
)
dest.add_argument("-u", "--user", help="The name of the user to send the message to.")
dest.add_argument(
    "-f",
    "--files",
    help="The path(s) to file(s) to send as an attachment.",
    nargs="+",
    default=None,
)
dest.add_argument(
    "-s",
    "--save-hook",
    help="Save the message hook to a file in order to be able to update it later. Provide a filename to save to.",
    default=None,
)
dest.add_argument(
    "--configfile",
    help="The path to a .mattermost_notify file or a directory containing such a file. By default Mattermost Notify will search in either $PWD or $HOME",
    default=None,
)

update.add_argument("message", help="The message to update.")
update.add_argument(
    "-n",
    "--team-name",
    help="The name of the team (the 'notify' bot needs to be a member!)",
    default=None
)
update.add_argument(
    "-f",
    "--hook",
    help="The file containing the message hook. That was saved when the message was sent.",
    required=True,
)
update.add_argument(
    "--configfile",
    help="The path to a .mattermost_notify file or a directory containing such a file. By default Mattermost Notify will search in either $PWD or $HOME",
    default=None,
)


test.add_argument(
    "--configfile",
    help="The path to a .mattermost_notify file or a directory containing such a file. By default Mattermost Notify will search in either $PWD or $HOME",
    default=None,
)
test.add_argument(
    "-n",
    "--team-name",
    help="The name of the team (the 'notify' bot needs to be a member!)",
    default=None
)


def main():
    args = parser.parse_args()

    if args.command == "setup":
        if args.interactive or not any([args.url, args.team_name, args.bot_name, args.token, args.ssl_verify]):
            from mattermost_notify.config import setup_config_interactive

            setup_config_interactive()
        else:
            from mattermost_notify.config import setup_config

            if args.output == "$HOME":
                args.output = None
            setup_config(args.url, args.team_name, args.bot_name, args.token, args.ssl_verify, args.output)

    elif args.command == "send":
        from mattermost_notify.client import Notify
        from mattermost_notify.config import get_config

        msg_id = str(uuid4())

        config = get_config(args.configfile)

        client = Notify(
            url=config["url"], team_name=config["team_name"], bot_name=config["bot_name"], token=config["token"],
            ssl_verify=config["ssl_verify"]
        )
        if args.channel:
            client.send_to_channel(
                args.message, channel_name=args.channel, files=args.files, id=msg_id
            )
        elif args.user:
            client.send_to_user(
                args.message, user_name=args.user, files=args.files, id=msg_id
            )

        if args.save_hook:
            client.write_message_hook_to_file(id=msg_id, filename=args.save_hook)

    elif args.command == "update":
        from mattermost_notify.client import Notify
        from mattermost_notify.config import get_config

        config = get_config(args.configfile)
        if args.team_name:
            config["team_name"] = args.team_name
        client = Notify(
            url=config["url"], team_name=config["team_name"], bot_name=config["bot_name"], token=config["token"],
            ssl_verify=config["ssl_verify"]
        )
        with open(args.hook, "r") as file:
            file.readline()
            msg_id = file.readline().strip()
        client.read_message_hook_from_file(args.hook)
        client.send_update(message=args.message, id=msg_id)

    elif args.command == "test":
        from mattermost_notify.client import Notify
        from mattermost_notify.config import get_config

        config = get_config(args.configfile)
        if args.team_name:
            config["team_name"] = args.team_name
        client = Notify(
            url=config["url"], team_name=config["team_name"], bot_name=config["bot_name"], token=config["token"]
        )
        assert client.test_connection(), "Connection failed"
        print("Connection successful!")

    else:
        parser.print_help()


if __name__ == "__main__":

    main()
