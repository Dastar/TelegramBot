import csv
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

from setup import CONFIGS, logger


# Replace these with your own values
phone = '+972503058777'
group_username = 't3chn3wsh3b1l'
config = CONFIGS.safe_read_configuration()

# Create and start the client
client = TelegramClient(phone, config['api_id'], config['api_hash'])


async def fetch_messages():
    await client.start()
    entity = await client.get_entity(group_username)
    my_channel = PeerChannel(entity.id)

    # Fetch the last 100 messages
    messages = await client(GetHistoryRequest(
        peer=my_channel,
        limit=100,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))

    # Extract message texts
    message_texts = set(msg.message for msg in messages.messages if msg.message)

    # Save to CSV
    with open('messages1.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Message'])
        for message in message_texts:
            writer.writerow([message])

    print("Messages saved to messages.csv")


# Run the async function
with client:
    client.loop.run_until_complete(fetch_messages())
