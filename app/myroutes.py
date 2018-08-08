from app import app
from flask import make_response
from flask import request
from app import messages
from app import spotlightbot 
from flask import render_template
import json
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os

bot = spotlightbot.SpotlightBot()


@app.route('/', methods=['GET'])
@app.route('/index')
def index():
    """ Return User friendly Hello message """
    
    return "Hello, Welcome to Spotlight BOT!"

@app.route('/hello', methods=['POST'])
def hello():
    """ Return Hello response """
    #print('Received Data ' + request.data.decode('utf-8'))
    print( request.form)
    return bot.hello_response(request.form)


@app.route("/handshake", methods=["GET", "POST"])
def handshake():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    bot.auth(code_arg)
    return render_template("thanks.html")

def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.
    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event
    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error
    """
    team_id = slack_event["team_id"]
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        # Send the onboarding message
        bot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200,)

    # ============== Share Message Events ============= #
    # If the user has shared the onboarding message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    elif event_type == "message" and slack_event["event"].get("attachments"):
        user_id = slack_event["event"].get("user")
        if slack_event["event"]["attachments"][0].get("is_share"):
            # Update the onboarding message and check off "Share this Message"
            bot.update_share(team_id, user_id)
            return make_response("Welcome message updates with shared message",
                                 200,)

    # ============= Reaction Added Events ============= #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "reaction_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        bot.update_emoji(team_id, user_id)
        return make_response("Welcome message updates with reactji", 200,)

    # =============== Pin Added Events ================ #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "pin_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        bot.update_pin(team_id, user_id)
        return make_response("Welcome message updates with pin", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if bot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], bot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

SLACK_VERIFICATION_TOKEN = os.environ["VERIFICATION"]
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events",app)

# Create a SlackClient for your bot to use for Web API requests
SLACK_BOT_TOKEN = os.environ["BOT_TOKEN"]
CLIENT = SlackClient(SLACK_BOT_TOKEN)

print('In Events Bot!')
# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    print('Inside Slack event adapter!')
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "SPOTL8" in str(message.get('text')).upper():
        channel = message["channel"]
        message = "Hello <@%s>! :tada: Welcome to Spotlight BOT!!" % message["user"]
        CLIENT.api_call("chat.postMessage", channel=channel, text=message)
    elif message.get("subtype") is None and "SPOTL8" not in str(message.get('text')).upper():        
        channel = message["channel"]
        message = "Cool Things are coming up! Stay Tuned <@%s>! :tada:" % message["user"]
        CLIENT.api_call("chat.postMessage", channel=channel, text=message)


# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    CLIENT.api_call("chat.postMessage", channel=channel, text=text)

if __name__ == '__main__':
   app.run(host='0.0.0.0')