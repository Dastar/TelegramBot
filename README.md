# Telegram Channel Translator Bot

This bot listens to specific Telegram channels for new messages, translates those messages using ChatGPT, and sends the translated messages to another specified channel.

## Features

- Listens to multiple Telegram channels for new messages.
- Translates messages using ChatGPT.
- Sends the translated messages to a specified Telegram channel.

## Requirements

- Python 3.8+
- `telethon` library
- `openai` library
- OpenAI API key
- Telegram API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/telegram-channel-translator-bot.git
    cd telegram-channel-translator-bot
    ```

2. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your configuration file:
    - Create a `config.ini` file in the /configurations folder.
    - Add your configuration details to the `config.ini` file:
    ```ini
    [DEFAULT]
    ApiKey = OpenAIApiKey
    ApiId = TelegramApiId
    ApiHash = TelegramApiHash
    SessionName = sessions_folder/session_name
    LogFile = logger.log
    LogLevel = INFO
    LogName = LOGNAME
    RoleFile = configurations/role.yaml
    ChannelsFile = configurations/ChannelRegistry.yaml
    ForwardMessage = {name}:{line}{line}
    ```

## Usage

1. Run the bot:
    ```bash
    python bot.py
    ```

2. The bot will start listening to the specified Telegram channels. When a new message appears, it will be translated and sent to the target channel.

## Configuration

## Example

## Notes

## License

## Contributing
