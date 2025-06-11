.. mattermost-notify documentation master file, created by
   sphinx-quickstart on Thu Jan 23 13:11:20 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Set up Mattermost Notify
========================

If you have not set up the Notify Bot yet, please refer to the `Notify Bot Setup`_ documentation.

.. _Notify Bot Setup: setup_bot

Once you have your Bot ready you can start using the Mattermost Notify package.

1. Install the Mattermost Notify package
----------------------------------------

The package can be installed via pip:

.. code:: bash
   
   # (yep it's in reverse since another project already used the name on PyPi 😅)
   pip install mattermost-tools


2. Set up the connection to your Mattermost server
--------------------------------------------------

To allow the Mattermost Notify package to connect to your Mattermost server, you need to provide the Bot's token and the server URL.
There is an interactive dialog that you can run by typing:

.. code:: bash

   mattermost-notify setup

Alternatively you can provide the required inputs directly from command-line like should

.. code:: bash

   mattermost-notify setup --token <your_token> --url <your_server_url> --team-name <the name of your team> --bot-name <the name of your bot> --ssl-verify <enable/disable ssl verification>


.. note::

   The `--url` should include the protocol (e.g. `https://`) at the beginning.

You can test the connection by running:

.. code:: bash

   mattermost-notify test

To test if your connection also works you can try sending a message to your user account

.. code:: bash

   mattermost-notify send "this is a test" --user <your_username> --team-name <your team name>

If you have set up the Notify Bot correctly, you should receive a direct message in your Mattermost application or browser session.

