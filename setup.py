from setuptools import setup, find_packages

setup(
    name="mattermost-tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "."},
    version="0.0.3",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
        "requests",
        "argparse", "websockets",
    ],
    entry_points={
        "console_scripts": [
            "mattermost-notify=mattermost_notify.cli:main", "mmstdin2channel=mattermost.stdin2channel:main"
        ],
    },
    author="Neil Karania",
    author_email="neil.karania19@gmail.com",
    description="A tool to send notifications to Mattermost and manage Mattermost channels and users.",
    license="MIT",
    url="https://github.com/neil-karania/mattermost-tools",
)
