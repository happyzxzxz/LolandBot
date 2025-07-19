# LolandBot

Music bot for discord. Made with [Lavalink](https://github.com/lavalink-devs/Lavalink), [Wavelink 3.0](https://github.com/PythonistaGuild/Wavelink) and plugins: [Lavasrc](https://github.com/topi314/LavaSrc), [Youtube-source](https://github.com/lavalink-devs/youtube-source)

### Features
- Youtube search as main music source, also supports vk music, yandex music, spotify, twitch and basically everything that [Lavasrc](https://github.com/topi314/LavaSrc) had implemented (including any audio files and some audio streams)
- Fully functional music player in discord
- Openai image and chat requests. Can chage API endpoint to use different provider
- Gelbooru api requests
- Saucenao api requests
- Flowery TTS api requests
- Reaction roles
- Custom server-personalized equalizer settings for the player
- Scripts to launch all this stuff automatically for windows and linux. Will add better deploy some time later

### What do you need?

- [Java Runtime Enviroment 17](https://www.oracle.com/java/technologies/downloads/) or newer
- [Python 3](https://www.python.org/)
- [wget](https://www.gnu.org/software/wget/) on linux or [curl](https://curl.se/) on windows (should be preinstalled already)

### Quick setup

1. Change variables in the `.env` file. Bare minimum is only `DISCORD_API_TOKEN`. If you don't want anything else, you can leave it untouched. You can get most of these keys somewhere at the provider site, openai.com for example. If you want `YANDEX_MUSIC_TOKEN` or spotify stuff, go to the [Lavasrc](https://github.com/topi314/LavaSrc) github page. VK token is [here](https://vkhost.github.io/)
2. In `settings.py` change values of the `ENABLED_COMMANDS` variable. Enable only that commands that you will use. It also makes sense to disable commands that requires some api keys that you didn't set up in the `.env`
3. Launch `setup_and_launch` file (bat/sh) depending on your os (this activates new python venv too)
4. Wait some time before bot will sync all commands and launch. Alternatively, you can launch bot with `python main.py` and Lavalink with `Java -jar Lavalink.jar`

### Authorization method

If you want to use **_Youtube_** or **_Spotify_** sources then you need to choose between one of the two available options:

1. #### Google OAuth (recommended)

- Will work for a long time but may be bad with a high traffic.
- Can get your account terminated! Use only with burner please
To use it, just launch lavalink one time (`setup_and_launch` or `launch_lavalink`) and then see Lavalink logs (current log is in the `Lavalink/logs/spring.log` file). There will be a link. Just auth with your google account and paste your refresh token in the `.env` where `YOUTUBE_REFRESH_TOKEN` is and then restart lavalink (`kill_lavalink` for example). Done.
See more [here](https://github.com/lavalink-devs/youtube-source?tab=readme-ov-file#using-oauth-tokens)

2. #### Potoken

- No need for any accounts
- Could be annoying to maintain, one token works for around 12 hours
- Works only with WEB and WEBEMBEDDED clients

See [This Page](https://github.com/lavalink-devs/youtube-source/?tab=readme-ov-file#using-a-potoken) for instructions. Right now there is no automatic support for it in this bot, but you can do it yourself