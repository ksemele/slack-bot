import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Dictionary to store button locks
button_locks = {}

# import re

# @app.message(re.compile("<!channel(|\^)>"))
# def message_channel(message, say):
#     # say() sends a message to the channel where the event was triggered
#     say(
#         f"Hey there <@{message['user']}>! You mentioned @channel in your message."
#     )

# @app.message(re.compile("<@U[A-Z0-9]+>"))
# def message_user(message, say):
#     # Get user ID from the mention
#     user_id = re.search("<@U([A-Z0-9]+)>", message["text"]).group(1)

#     # say() sends a message to the channel where the event was triggered
#     say(
#         f"Hey there <@{message['user']}>! You mentioned <@{user_id}> in your message."
#     )

# Listens to incoming messages that contain the command "/help"
@app.command("/help")
def command_help(ack, respond):
    # Acknowledge command request
    ack()

    # Send message with instructions
    respond(
        "Hi there! Here are the available commands:\n"
        "/help - Show this message\n"
    )

@app.message(re.compile("<@U[A-Z0-9]+>"))
def message_user(message, say):
    # Get user ID from the mention
    user_id = re.search("<@U([A-Z0-9]+)>", message["text"]).group(1)

    # Get user info from Slack API
    user_info = app.client.users_info(user=user_id)

    # Get user name
    user_name = user_info["user"]["name"]

    # say() sends a message to the channel where the event was triggered
    say(
        f"Hey there <@{message['user']}>! You mentioned @{user_name} in your message."
    )



# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # Get user ID
    user_id = message['user']

    # Check if button is already locked for this user
    if button_locks.get(user_id, False):
        say(f"Sorry <@{user_id}>, the button is not available now.")
        return

    # Lock the button for this user
    button_locks[user_id] = True

    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{user_id}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click",
                    "style": "primary"
                }
            }
        ],
        text=f"Hey there <@{user_id}>!"
    )

@app.action("button_click")
def action_button_click(body, ack, say):
    # Get user ID and action ID
    user_id = body['user']['id']
    action_id = body['actions'][0]['action_id']

    # Check if button is already locked for this user
    if not button_locks.get(user_id, False):
        return

    # Acknowledge the action
    ack()

    # Send message
    say(f"<@{user_id}> clicked the button")

    # Update message with new button text and style
    app.client.chat_update(
        channel=body['channel']['id'],
        ts=body['message']['ts'],
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{body['user']['id']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Request Processed"},
                    "action_id": "button_click",
                    "style": "danger"
                }
            }
        ]
    )

    # Unlock the button for this user
    button_locks[user_id] = False

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
