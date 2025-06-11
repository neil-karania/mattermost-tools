"""
Config utility
"""

from pathlib import Path

CONFIGFILENAME = ".mattermost_notify"

DEFAULT_HOME_LOCATION = Path.home() 

def search_config(path: Path = None):
    """
    Search for the configuration file

    Parameters
    ----------
    path : Path
        The path to search in

    Returns
    -------
    Path
        The path to the configuration file
    """
    if path is not None and Path(path).name == CONFIGFILENAME:
        return Path(path)
    if path is None:
        path = Path.cwd()
    if (path / CONFIGFILENAME).exists():
        return path / CONFIGFILENAME
    if path == Path.cwd():
        path = DEFAULT_HOME_LOCATION
    if (path / CONFIGFILENAME).exists():
        return path / CONFIGFILENAME
    raise FileNotFoundError(f"Could not find {CONFIGFILENAME} in {Path.cwd()} or {DEFAULT_HOME_LOCATION}")

def get_config(path: Path = None) -> dict:
    """
    Get the configuration from the configuration file

    Parameters
    ----------
    path : Path
        The path to the configuration file

    Returns
    -------
    dict
        The configuration
    """
    path = search_config(path)
    with open(path, "r") as file:
        lines = file.readlines()
    config = {}
    for line in lines:
        key, value = line.strip().split("=")
        config[key.lower()] = value
    return config

def setup_config(url: str, team_name: str, bot_name: str, token: str, ssl_verify: bool = True, directory: str = None):
    """
    Setup the configuration file

    Parameters
    ----------
    url : str
        The URL of the Mattermost server
    team_name : str
        The name of the team
    bot_name : str
        The name of the bot
    ssl_verify : bool
        SSL verification flag
    token : str
        The access token for the bot
    directory : str
        The path to write the configuration file to
    """
    if directory is None:
        directory = DEFAULT_HOME_LOCATION
    if isinstance(directory, str):
        if "$HOME" in directory:
            directory = directory.replace("$HOME", str(DEFAULT_HOME_LOCATION))
        if "~" in directory:
            directory = directory.replace("~", str(DEFAULT_HOME_LOCATION))
        if "$PWD" in directory:
            directory = directory.replace("$PWD", str(Path.cwd()))
    directory = Path(directory)
    with open(directory / CONFIGFILENAME, "w") as file:
        file.write(f"URL={url}\n")
        file.write(f"TEAM_NAME={team_name}\n")
        file.write(f"BOT_NAME={bot_name}\n")
        file.write(f"TOKEN={token}\n")
        file.write(f"SSL_VERIFY={ssl_verify}\n")

def setup_config_interactive():
    """
    Setup the configuration file interactively
    """
    url = input("Enter the URL of the Mattermost server: ")
    team_name = input("Enter the name of the team: ")
    bot_name = input("Enter the name of the bot: ")
    token = input("Enter the access token for the bot: ")
    ssl_verify = not input("Enable ssl verification y/n: ") == "n"
    setup_config(url, team_name, bot_name, token, ssl_verify)
    print("Configuration written to", DEFAULT_HOME_LOCATION / CONFIGFILENAME)
