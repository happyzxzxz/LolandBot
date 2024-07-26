# LolandBot

Music bot for discord. Made with [Lavalink](https://github.com/lavalink-devs/Lavalink), [Wavelink 3.0](https://github.com/PythonistaGuild/Wavelink) and plugins: [Lavasrc](https://github.com/topi314/LavaSrc), [Youtube-source](https://github.com/lavalink-devs/youtube-source)

### Features
- Youtube search as main music source, also supports vk music, yandex music, spotify, twitch and much more (including any audio files and some audio streams)
- Fully functional music player in discord
- Openai image and chat requests
- Gelbooru api requests
- Saucenao api requests
- Flowery TTS api requests
- Reaction roles

### What do you need?

- [Java Runtime Enviroment](https://www.oracle.com/java/technologies/downloads/)
- [Python 3](https://www.python.org/)

### Quick setup

1. Change variables in the `.env` file. Bare minimum is only `DISCORD_API_TOKEN`. If you don't want anything else, you can leave it untouched. You can get most of these keys somewhere at the provider site, openai.com for example. If you want `YANDEX_MUSIC_TOKEN` or spotify stuff, go to the [Lavasrc](https://github.com/topi314/LavaSrc) github page. VK token is [here](https://vkhost.github.io/)
2. In `settings.py` change values of the `ENABLED_COMMANDS` variable. Enable only that commands that you will use. It also makes sense to disable commands that requires some api key that you didn't set up in the `.env`
3. Launch `setup_and_launch` file (bat/sh) depending on your os (this activates new venv too)
4. Wait some time before bot will sync all commands and launch

Alternatively, you can launch bot with `python main.py` and Lavalink with `Java -jar Lavalink.jar`

