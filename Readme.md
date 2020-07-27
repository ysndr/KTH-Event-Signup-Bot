# Event signup bot for Discord

Bot to manage event signups on the unofficial KTH Admitted Students 2020 Discord server


## Setup

1. Create a bot user in Discord developer interface
2. give it `268561488` permissions
3. Copy the token, you need it in the next step

## Installation

1. The environment of this bot is managed using [`nix`](https://nixos.org/nix). On a nix system you can just run `nix-shell nix/shell.nix`.
   On other systems either install nix or use any other way to install python as well as the `discordpy` and `python-dotenv` package using `pip` (You might wnat to consider a virtualenv for this).
2. copy `example.env` to `.env` and adapt too your server, insert the token you got before.
3. Finally run the bot using `python bot.py`

## Usage

The bot currently supports one command `event`. Commands are executed by starting a message with `$ ` (notice the space, i.e. `$ event`)
If you use `@mentions` put them in braces so that they are not decomposed into `< @ ! 505120366977482763 >`
