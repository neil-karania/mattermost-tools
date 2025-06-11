"""
The main client to connect to a Mattermost Server
"""

import requests
from pathlib import Path


class MessageUpdator:
    def __init__(
        self, text: str, client: "Notify", channel_id: str, message_id: str, id: str, ssl_verify: bool
    ):
        self.client = client
        self.channel_id = channel_id
        self.message_id = message_id
        self.text = text
        self.id = id
        self.ssl_verify = ssl_verify

    def update(self, message: str):
        data = {
            "id": self.message_id,
            "channel_id": self.channel_id,
            "message": message,
        }
        response = requests.put(
            self.client.endpoint(f"posts/{self.message_id}"),
            headers=self.client.headers,
            json=data, verify=self.ssl_verify,
        )
        self.text = message
        return response.status_code == 200

    def write_to_file(self, filename):
        with open(filename, "w") as f:
            f.write(
                f"""
[Mattermost-Notify Message Hook]
{self.id}
{self.channel_id}
{self.message_id}
                    """.strip()
            )


class PermissionError(Exception):
    pass


BOT_NAME = "notify"


class Notify:
    """
    The main client for the Mattermost Notify Bot

    Parameters
    ----------
    url : str
        The URL of the Mattermost server
    token : str
        The access token for the bot
    team_name : str, optional
        The name of the team, by default None
    bot_name : str, optional
        The name of the bot, by default 'notify'
    """

    def __init__(self, url: str, token: str, team_name: str = None, bot_name: str = None, ssl_verify: bool = True):
        self._api_url = url.rstrip("/") + "/api/v4"
        self._team_name = team_name
        self.__access_token = token
        self.__default_channel_id = None
        self.__cache = {
            "user_ids": {},
            "channel_ids": {},
            "direct_message_channels": {},
            "sent_messages": {},
        }
        self.__ssl_verify = ssl_verify
        self.__team_id = self.__get_team_id(team_name)
        self.__own_user_id = self.__get_user_id(bot_name if bot_name else BOT_NAME)

    def test_connection(self) -> bool:
        """
        Test the connection to the Mattermost server

        Returns
        -------
        bool
            True if the connection is successful
        """
        response = requests.get(self.endpoint("users"), headers=self.headers, verify=self.__ssl_verify)
        try:
            response_json = response.json()
            return response.status_code == 200
        except requests.exceptions.JSONDecodeError:
            print("Failed to decode JSON response")
            print(response.text)  # Print the raw response text for debugging
            return False

    def set_default_channel(self, channel_name: str):
        """
        Set the default channel to send messages to

        Parameters
        ----------
        channel_name : str
            The name of the channel
        """
        self.__default_channel_id = self.__get_channel_id(channel_name)

    def endpoint(self, path: str):
        """
        Get the full URL for an API endpoint

        Parameters
        ----------
        path : str
            The path to the endpoint
        """
        return f"{self._api_url}/{path}"

    def message_in_cache(self, id: str) -> bool:
        """
        Check if a message with a given ID is in the cache

        Parameters
        ----------
        id : str
            The ID to check

        Returns
        -------
        bool
            True if the message is in the cache
        """
        return id in self.__cache["sent_messages"]

    def write_message_hook_to_file(self, id: str, filename: str):
        """
        Write a message-hook from cache to file so that it can be loaded and updated even from another client instance.

        Parameters
        ----------
        id : str
            The ID of the message
        filename : str
            The name of the file to write to
        """
        self.__cache["sent_messages"][id].write_to_file(filename)

    def read_message_hook_from_file(self, filename: str):
        """
        Read a message-hook from a file so that it can be updated.

        Parameters
        ----------
        filename : str
            The name of the file to read from
        """
        with open(filename, "r") as f:
            lines = f.readlines()
        id = lines[1].strip()
        channel_id = lines[2].strip()
        message_id = lines[3].strip()
        self.__cache["sent_messages"][id] = MessageUpdator(
            "", self, channel_id, message_id, id, self.__ssl_verify
        )

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.__access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Safari/537.3 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110",
        }

    def __get_user_id(self, username: str) -> str:
        """
        Get the user ID for a given username

        Parameters
        ----------
        username : str
            The username to look up

        Returns
        -------
        str
            The user ID
        """
        if username in self.__cache["user_ids"]:
            return self.__cache["user_ids"][username]

        response = requests.get(
            self.endpoint(f"users/username/{username}"), headers=self.headers, verify=self.__ssl_verify
        )
        user_id = response.json()["id"]
        self.__cache["user_ids"][username] = user_id
        return user_id

    def __get_team_id(self, team_name: str) -> str:
        """
        Get the team ID for a given team name

        Parameters
        ----------
        team_name : str
            The team name to look up

        Returns
        -------
        str
            The team ID
        """
        response = requests.get(
            self.endpoint(f"teams/name/{team_name}"), headers=self.headers, verify=self.__ssl_verify
        )
        if response.status_code == 403:
            raise PermissionError(
                "You do not have permission to access this team. Provide a token with the correct permissions."
            )
        return response.json()["id"]

    def __get_channel_id(self, channel_name: str) -> str:
        """
        Get the channel ID for a given channel name

        Parameters
        ----------
        channel_name : str
            The channel name to look up

        Returns
        -------
        str
            The channel ID
        """
        if channel_name in self.__cache["channel_ids"]:
            return self.__cache["channel_ids"][channel_name]
        response = requests.get(
            self.endpoint(f"teams/{self.__team_id}/channels/name/{channel_name}"),
            headers=self.headers, verify=self.__ssl_verify
        )
        channel_id = response.json()["id"]
        self.__cache["channel_ids"][channel_name] = channel_id
        return channel_id

    def __get_direct_message_channel_id(self, user_id: str) -> str:
        """
        Get the direct message channel ID for a given user ID

        Parameters
        ----------
        user_id : str
            The user ID to look up

        Returns
        -------
        str
            The direct message channel ID
        """
        if user_id in self.__cache["direct_message_channels"]:
            return self.__cache["direct_message_channels"][user_id]
        response = requests.post(
            self.endpoint("channels/direct"),
            headers=self.headers,
            json=[user_id, self.__own_user_id],
        )
        channel_id = response.json()["id"]
        self.__cache["direct_message_channels"][user_id] = channel_id
        return channel_id

    def __send_file_to_channel(self, file_path: str, channel_id: str):
        """
        Send a file to a channel

        Parameters
        ----------
        file_path : str
            The path to the file to send
        channel_id : str
            The ID of the channel to send the file to
        """
        data = {
            "channel_id": ("", channel_id),
            "client_ids": ("", "id_for_file"),
            "files": (Path(file_path).name, open(file_path, "rb")),
        }
        headers = self.headers
        del headers["Content-Type"]  # = "multipart/form-data
        response = requests.post(self.endpoint("files"), files=data, headers=headers, verify=self.__ssl_verify)
        if not response.status_code == 201:
            raise ValueError("Failed to upload file")
        file_id = response.json()["file_infos"][0]["id"]
        data = {"channel_id": channel_id, "file_ids": [file_id]}
        response = requests.post(
            self.endpoint("posts"), headers=self.headers, json=data, verify=self.__ssl_verify
        )
        return response.status_code == 201

    def __send_file_to_user(self, file_path: str, user_id: str):
        """
        Send a file to a user

        Parameters
        ----------
        file_path : str
            The path to the file to send
        user_id : str
            The ID of the user to send the file to
        """
        if user_id in self.__cache["direct_message_channels"]:
            channel_id = self.__cache["direct_message_channels"][user_id]
        else:
            channel_id = self.__get_direct_message_channel_id(user_id)
        data = {
            "channel_id": ("", channel_id),
            "client_ids": ("", "id_for_file"),
            "files": (Path(file_path).name, open(file_path, "rb")),
        }
        headers = self.headers
        del headers["Content-Type"]
        response = requests.post(self.endpoint("files"), files=data, headers=headers, verify=self.__ssl_verify)
        if not response.status_code == 201:
            raise ValueError("Failed to upload file")
        file_id = response.json()["file_infos"][0]["id"]
        data = {"channel_id": channel_id, "file_ids": [file_id]}
        response = requests.post(
            self.endpoint("posts"), headers=self.headers, json=data, verify=self.__ssl_verify
        )
        return response.status_code == 201

    def send_to_channel(
        self,
        message: str,
        channel_name: str = None,
        files: list = None,
        id: str = None,
    ):
        """
        Send a message to a channel

        Parameters
        ----------
        message : str
            The message to send
        channel_name : str, optional
            The name of the channel to send the message to, by default None
        files: list, optional
            A list of file paths to send to the channel, by default None.
        id: str, optional
            An identifier for the message in case you want to update it later.
        """
        if channel_name is None:
            channel_id = self.__default_channel_id
            if not channel_id:
                raise ValueError(
                    "No default channel set. Please provide a channel name."
                )
        else:
            channel_id = self.__get_channel_id(channel_name)

        data = {"channel_id": channel_id, "message": message}
        response = requests.post(
            self.endpoint("posts"), headers=self.headers, json=data, verify=self.__ssl_verify
        )
        if files is not None:
            for file in files:
                self.__send_file_to_channel(file, channel_id)

        if id:
            self.__cache["sent_messages"][id] = MessageUpdator(
                message, self, channel_id, response.json()["id"], id
            )

        return response.status_code == 201

    def send_to_user(
        self,
        message: str,
        user_name: str,
        files: list = None,
        id: str = None,
    ):
        """
        Send a direct message to a user

        Parameters
        ----------
        message : str
            The message to send
        user_name : str
            The username of the recipient
        files: list, optional
            A list of file paths to send to the user, by default None.
        id: str, optional
            An identifier for the message in case you want to update it later.
        """
        user_id = self.__get_user_id(user_name)
        if user_id in self.__cache["direct_message_channels"]:
            channel_id = self.__cache["direct_message_channels"][user_id]
        else:
            channel_id = self.__get_direct_message_channel_id(user_id)
        data = {"channel_id": channel_id, "message": message}

        response = requests.post(
            self.endpoint("posts"), headers=self.headers, json=data, verify=self.__ssl_verify
        )
        if files is not None:
            for file in files:
                self.__send_file_to_user(file, user_id)

        if id:
            self.__cache["sent_messages"][id] = MessageUpdator(
                message, self, channel_id, response.json()["id"], id
            )

        return response.status_code == 201

    def send_update(
        self,
        message: str,
        id: str,
    ):
        """
        Update a message that was sent earlier

        Parameters
        ----------
        message : str
            The new message
        id : str
            The identifier of the message that was set when sending the message
        """
        if id not in self.__cache["sent_messages"]:
            raise ValueError("Message not found")
        return self.__cache["sent_messages"][id].update(message)
