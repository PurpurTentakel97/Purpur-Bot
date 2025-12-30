# Tentakel Bot

## Features:
- Twitch and Discord integration
- Multiple permission levels
- Multiple Bot Instances

## Configuration:
### .env file:
The .env file should be located in the root directory. You can use the [example](.env.sample) as a template.
Add at least one of the Discord or Twitch credentials.
The Bot is fully functional if you only support one platform. The other bot will just not start.
Twitch's tokens will be updated automatically within the .env file.

### config file:
There should be a config.json in the root directory. If not, start the bot once, and it will be created.
The generated config will look something like this: (0.0.1):

```json
{
  "version": "0.0.1",
  "user": [
    {
      "id": 0,
      "name": "default",
      "twitch": [
        "twitch_channel_name"
      ],
      "discord": [
        0
      ]
    }
  ]
}
```

The list within the user tag can be extended to create multiple bots.
Within the twitch tag you can add multiple twitch channels by their name.
Within the discord tag you can add multiple discord servers by their id. When you don't know the id: let the bot join your server and run the bot. The bot will mark messages vom that server with the server_id within the console.

**NOTE:** The ID will be used within the database. Make sure it is unique within your bot configuration. And make sure it will not change over time.

## Permission Levels:
### general Permission Levels:
1. Admin
2. Moderator
3. Special User
4. User

### Permission mapping per Platform:
#### Twitch:
    - Admin: when the broadcaster batch is present
    - Moderator: Twitchs Moderator role
    - Special User: Twitchs vip role
    - User: enyone else
#### Discord:
    - Admin: Server Member with admin rights
    - Moderator: Server Member with manage messages permission
    - Special User: Server Member with "vip" or "VIP" role
    - User: enyone else
