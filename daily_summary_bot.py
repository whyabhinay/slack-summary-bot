import os
from datetime import datetime, timedelta
from slack_sdk import WebClient
from dotenv import load_dotenv
import logging
import requests

# Load environment variables
load_dotenv()

# Initialize Slack client
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)

# Configure logging
logging.basicConfig(
    filename='messages.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Function to fetch yesterday's messages
def fetch_yesterdays_messages(channel_id: str):
    yesterday = datetime.now() - timedelta(days=1)
    response = client.conversations_history(
        channel=channel_id,
        oldest=yesterday.timestamp(),
        latest=datetime.now().timestamp()
    )
    messages = response['messages']

    # Print messages for debugging
    print("Fetched Messages:")
    for msg in messages:
        print(f"User {msg.get('user')}: {msg.get('text')}")

    # Log messages for debugging
    logging.info("Fetched Messages:")
    for msg in messages:
        logging.info(f"User {msg.get('user')}: {msg.get('text')}")

    return messages

# Function to summarize messages using your local LLM
def summarize_messages(messages):
    # Combine all messages into a single string
    combined_messages = "\n".join([f"User {msg.get('user')}: {msg.get('text')}" for msg in messages])

    # Call your local LLM API to summarize
    llm_api_url = 'http://localhost:5000/summarize'
    response = requests.post(llm_api_url, json={'text': combined_messages})
    return response.json().get('summary', 'No summary available.')

# Function to post the summary to Slack
def post_summary(channel_id: str, summary: str):
    client.chat_postMessage(
        channel=channel_id,
        text=f"Here's the summary of yesterday's messages:\n\n{summary}"
    )

# Daily summary task
def daily_summary():
    channel_id = 'your-channel-id'  # Replace with your channel ID
    messages = fetch_yesterdays_messages(channel_id)
    summary = summarize_messages(messages)
    post_summary(channel_id, summary)

if __name__ == '__main__':
    daily_summary()