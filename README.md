# Tentakel Bot

## Getting Started

First, you don't need to host the bot yourself.
You can use the [hosted version](https://purpur-bot.coder2k.net).
But you are welcome to host it yourself if you want to.

Thanks to [coder2k](https://github.com/mgerhold) that I'm allowed to host the bot on his server.

### UV Setup

| Description        | Command                                                             |
|--------------------|---------------------------------------------------------------------|
| install uv         | ``pip install uv``                                                  |
| setup dependencies | ``uv sync``                                                         |
| start the bot      | ``uv run --no-dev uvicorn --host 0.0.0.0 --port 8000 bot.main:app`` |
| start check        | ``uv run poe check``                                                |
| start fix          | ``uv run poe fix``                                                  |
| start test         | ``uv run poe test``                                                 |

### Docker Setup

This is a production-ready docker setup. No development setup.

| Description        | Command                    |
|--------------------|----------------------------|
| build docker image | ``docker compose build``   |
| start docker image | ``docker compose up -d``   |
| show docker logs   | ``docker compose logs -f`` |

### Deployed Version:

Modify the .env file to your needs.
You can either use the current docker setup and build the docker image yourself with docker compose on the server.
Or you can modify the [docker compose file](docker-compose.yml) to download the last version from GitHub.
Then you only need the docker compose file and the .env file on your server and start it.
The GitHub URl is: `` image: ghcr.io/purpurtentakel97/purpur-bot:<version>``. The version is the release tag on GitHub
or `nightly`
I recomend to add a second port where you can dedicate run the Twitch subscriptions. Seams to make things a lot easier.

### .env file:

The .env file should be located in the root directory. You should use the [example](.env.sample) as a template.
Add at least one of the Discord or Twitch credentials.
The Bot is fully functional if you only support one platform. The other bot will just not start.
Twitch's tokens will be updated automatically within the .env file.

## Features:

### General:

The Bot connects to Twitch and Discord individually.
It reacts to Discord and Twitch Messages.
It can connect to multiple Twitch channels and Discord servers.
It can handle multiple Bot instances.
Nearly all features are able to turn on and off via the web interface.

### Web Interface:

The Bot has a web interface.
It can be used to manage the Bot.
The web interface needs at least a Twitch OAuth login to set up a bot.
If you also want to use the bot on a Discord server, you also need a Discord OAuth login.
To set up a bot and let a bot join some channels, you need to use the web interface.

### Build in Commands:

The Bot has some build in commands.
This can be used to manage the Bot via Discord and Twitch chats.
Not all features are available via the build in commands.
If a command is not available, use the web interface.
A table of all commands can be found in the build in the commands section.

### Custom Commands

The bot has custom commands.
These can be managed via the web interface and the build in commands.
The commands can handle counter. The counter-syntax will be explained in the counter-section file.

### Counter

The bot has a counter-system.
This can be used to handle counter within the custom commands.
The Syntax for the counter is explained in the counter-section.

### Broadcast Messages:

The Bot can send custom messages to specific Twitch chats in a custom interval.

### Aliases:

The bot can handle aliases.
The bot will respond with an explanation when the registered word appears within a message.

### Cooldowns:

The bot has cooldowns for commands, aliases and online messages.
All cooldowns are in seconds and global.
You can change it in the .env file.

### Online Messages:

The bot can send a message to a specific Discord channel when a twitch channel goes online.
Use '@' to mention a role; e.g. `@live`. The bot will try to resolve the role id from the role name.
Note: This is case-sensitive. ``@everyone`` and ``@here`` gets ignored by the bot since this triggers within discord
without the id.

## Permission Levels:

### general Permission Levels:

1. Admin
2. Moderator
3. Special User
4. User

### Permission mapping per Platform:

#### Twitch:

- Admin: when the broadcaster batch is present
- Moderator: Twitches Moderator role
- Special User: Twitches vip role
- User: anyone else

#### Discord:

- Admin: Server Member with admin rights
- Moderator: Server Member with manage messages permission
- Special User: Server Member with "vip" or "VIP" role
- User: anyone else

## Build in Commands:

- '*' -> ignores all remaining words
- '<>' -> variable
- '<*>' -> captures all remaining words

| Commands                                       | Description                                                                                  | Min Permission Level |
|------------------------------------------------|----------------------------------------------------------------------------------------------|----------------------|
| !title \<title*\>                              | Sets the Twitch Title from the Chat it was send in. Note: Max 140 Characters                 | Mod                  |
| !game \<category*\>                            | Sets the Twitch Category from the Chat it was send in.                                       | Mod                  |
| !tags \<tags*\>                                | Sets the Twitch Tags from the Chat it was send in. Note: max 10 Tags with max 25. Characters | Mod                  |
| !com add \<name\> \<message*\>                 | Adds a custom command (this will add a counter if one is added)                              | VIP                  |
| !com edit_name \<old_name\> \<new_name\> *     | Edits a custom command name                                                                  | VIP                  |
| !com edit_message \<name\> \<message*\>        | Edits a custom command message (this will add a counter if one is added)                     | VIP                  |
| !com enable \<name\> *                         | Enables a custom command                                                                     | VIP                  |
| !com disable \<name\> *                        | Disables a custom command                                                                    | VIP                  |
| !com remove \<name\> *                         | Deletes a custom command                                                                     | VIP                  |
| !com *                                         | prints a list of command related commands                                                    | VIP                  |
| !counter add \<name\> *                        | Adds a counter and initialze it with 0                                                       | VIP                  |
| !counter reset \<name\> *                      | Resets a counter to 0                                                                        | VIP                  |
| !counter show \<name\> *                       | Prints the current value of a counter                                                        | VIP                  |
| !counter edit_name \<old_name\> \<new_name\> * | Sets a new name for a counter                                                                | VIP                  |
| !counter edit_count \<name\> \<value\> *       | Sets the count of a counter to a specified value                                             | VIP                  |
| !counter increment \<name\> *                  | Increments a counter by 1                                                                    | VIP                  |
| !counter increment_by \<name\> \<value\> *     | Increments a counter by a specified value                                                    | VIP                  |
| !counter decrement \<name\> *                  | Decrements a counter by 1                                                                    | VIP                  |
| !counter decrement_by \<name\> \<value\> *     | Decrements a counter by a specified value                                                    | VIP                  |
| !counter remove \<name\> *                     | Removes a counter if it is unused                                                            | VIP                  |
| !counter *                                     | Prints a list of counter related commands                                                    | VIP                  |
| !alias add \<alias\> \<message*\>              | Adds an alias                                                                                | VIP                  |
| !alias edit_name \<old_alias\> \<new_alias\> * | Edits an alias                                                                               | VIP                  |
| !alias edit_message \<alias\> \<message*\>     | Edits an alias message                                                                       | VIP                  |
| !alias enable \<alias\> *                      | Enables an alias                                                                             | VIP                  |
| !alias disable \<alias\> *                     | Disables an alias                                                                            | VIP                  |
| !alias remove \<alias\> *                      | Removes an alias                                                                             | VIP                  |
| !alias *                                       | Prints a list of dictionary related commands                                                 | VIP                  |
| !quote add \<mension user\> <\msg*\>           | Adds a new quote for the mensioned user. Note: The quote gets stored plattform specific      | User                 |
| !quote <\mension user\> *                      | Prints a random quote from a specific user. Note: This is not working accross plattforms     | User                 |
| !quote *                                       | Prints a random quote. Note: This is working accross platforms                               | User                 |
| !coms *                                        | Prints a list of all commands                                                                | User                 |
| !<name> *                                      | If no build in commands triggers, executes the custom command                                | User                 |

## Counter

Counter can be used within custom commands.
Counters are integers that can be incremented, decremented or displayed.
They can turn positive and negative.

| Syntax                | Example                        | Description                                                    |
|-----------------------|--------------------------------|----------------------------------------------------------------|
| {\<name\>}            | Naya claped {counter} times.   | Displays the current value of a counter                        |
| {\<name\>+\<value\> } | Naya claped {counter+1} times. | Increments a counter by a specified value before displaying it |
| {\<name\>-\<value\> } | Naye claped {counter-1} times. | Decrements a counter by a specified value before displaying it |

Tipp:
You can increment or decrement a counter by any value, so `{counter+4711}` is valid. 
