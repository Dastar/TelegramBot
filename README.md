# Telegram ChatGPT Bot

This bot listens to specific Telegram channels for new messages, send those messages using ChatGPT with predifined roles, and sends the GPT respons to another specified channel.

## Features

- Listens to multiple Telegram channels for new messages.
- Translates messages using ChatGPT.
- Sends the translated messages to a specified Telegram channel.

## Requirements

See requirements.txt file

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
    LogFormat = 
    BotConfig = configurations/dummy.yaml
    ForwardMessage = {name}:{line}{line}
    ```
    - Make sure to properly define correct pathes for bot configuration file (see p4) and for session file (created by telethon).

4. Set up your bot configuration file:
   - Create a `dummy.yaml` file in the \configuration folder.
   - Add your configurations in the file:
   ```yaml
   roles:
   - id: 1
     name: homo
     system: You are homo from New York
     user: |
       This GPT is a homeless men from %%CITY%%. This GPT should answer for every question like homeless man does.
       Output only the actual answer. Your question is: \n\n%%TEXT%%

   channels:
   - name: algo_everyday
     target: target_channel_without_at
     monitored: monitored_channel1;monitored_channel2;
     role: homo
     model: gpt-4o
     tags: {CITY: New York, PLATFORM: Telegram}
   ```

## Usage

1. Run the bot:
    ```bash
    python main.py
    ```

2. The bot will start listening to the specified Telegram channels. When a new message appears, it will be translated and sent to the target channel.

## Configuration

## Example

## Notes

## License

## Contributing
