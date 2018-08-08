""" Spotlight Bot functions are defined here"""
import datetime
import logging
import random
import time
from flask import request
from flask import make_response
from app import messages
from slackclient import SlackClient
import os
from os.path import join, dirname
from dotenv import load_dotenv
from string import punctuation
from slackeventsapi import SlackEventAdapter

authed_teams = {}
class SpotlightBot(object):  
    
    def __init__(self):
        super(SpotlightBot, self).__init__()
        self.name = 'spotlight'
        self.emoji = ':robot_face:'
        self.oauth = {'client_id': os.getenv('CLIENT_ID'),#'2184481876.406675110357',#
                        'client_secret': os.getenv('CLIENT_SECRET'),#'cd10fcfb3f05b86be8c204b01a057c60',
                        'scope': ''}
        self.verification = os.getenv('VERIFICATION')
        self.bot_oauth_token = os.getenv('BOT_TOKEN')
        self.client = SlackClient(os.getenv('OAUTH_TOKEN'))#'xoxp-2184481876-237782784784-407624284916-eea9b05203d2f4c2f420f50f6f83cd24')      
        self.messages = {}

    def auth(self, authCode):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                'oauth.access',
                                client_id=self.oauth['client_id'],
                                client_secret=self.oauth['client_secret'],
                                code=authCode
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response['team_id']        
        authed_teams[team_id] = {'bot_token': auth_response['bot']['bot_access_token']}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]['bot_token'])
        self.messages = {}


    def hello_response(self,request):
        print('In Bot Hello Response!')
        #mess = str(request['token'])
        #print(mess)
        #print((self.verification))
        #print(type(self.verification))
        if str(request['token']) != str(self.verification):
           return make_response(messages.INVALID_TOKEN, 200,)
        try:
            input_message = str(request['text'])
        except Exception as e:
            print(e)
            return make_response(messages.ERROR,200)
           # print(str(request))
           # print(request)
           
        
        #print(input_message)
        if str.strip(input_message.upper()) == 'HELLO':    
                hello = messages.HELLO
        else:
                hello = messages.GENERIC_RESPONSE 

            # print(hello)
        response =  hello
        return make_response(response,200)

    def open_dm(self, user_id):
            """
            Open a DM to send a welcome message when a 'team_join' event is
            recieved from Slack.
            Parameters
            ----------
            user_id : str
                id of the Slack user associated with the 'team_join' event
            Returns
            ----------
            dm_id : str
                id of the DM channel opened by this method
            """
            new_dm = self.client.api_call("im.open",
                                        user=user_id)
            dm_id = new_dm["channel"]["id"]
            return dm_id



    def onboarding_message(self, team_id, user_id):
            """
            Create and send an onboarding welcome message to new users. Save the
            time stamp of this message on the message object for updating in the
            future.
            Parameters
            ----------
            team_id : str
                id of the Slack team associated with the incoming event
            user_id : str
                id of the Slack user associated with the incoming event
            """
            # We've imported a Message class from `message.py` that we can use
            # to create message objects for each onboarding message we send to a
            # user. We can use these objects to keep track of the progress each
            # user on each team has made getting through our onboarding tutorial.

            # First, we'll check to see if there's already messages our bot knows
            # of for the team id we've got.
            if self.messages.get(team_id):
                # Then we'll update the message dictionary with a key for the
                # user id we've recieved and a value of a new message object
                
                # ST Commented self.messages[team_id].update({user_id: message.Message()})
                self.messages[team_id].update({user_id: messages.TEAM_NOTE})
            else:
                # If there aren't any message for that team, we'll add a dictionary
                # of messages for that team id on our Bot's messages attribute
                # and we'll add the first message object to the dictionary with
                # the user's id as a key for easy access later.
                # self.messages[team_id] = {user_id: message.Message()}
                self.messages[team_id] = {user_id: messages.GENERIC_RESPONSE}
            message_obj = self.messages[team_id][user_id]
            # Then we'll set that message object's channel attribute to the DM
            # of the user we'll communicate with
            message_obj.channel = self.open_dm(user_id)
            # We'll use the message object's method to create the attachments that
            # we'll want to add to our Slack message. This method will also save
            # the attachments on the message object which we're accessing in the
            # API call below through the message object's `attachments` attribute.
            message_obj.create_attachments()
            post_message = self.client.api_call("chat.postMessage",
                                                channel=message_obj.channel,
                                                username=self.name,
                                                icon_emoji=self.emoji,
                                                text=message_obj.text,
                                                attachments=message_obj.attachments
                                                )
            timestamp = post_message["ts"]
            # We'll save the timestamp of the message we've just posted on the
            # message object which we'll use to update the message after a user
            # has completed an onboarding task.
            message_obj.timestamp = timestamp

    def update_emoji(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "reaction_added"
        event from Slack. Update timestamp for welcome message.
        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event
        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                            "~*Add an emoji reaction to this "
                                            "message*~ :thinking_face:",
                                    "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.emoji_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_pin(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "pin_added"
        event from Slack. Update timestamp for welcome message.
        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event
        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                            "~*Pin this message*~ "
                                            ":round_pushpin:",
                                    "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.pin_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_share(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "message" event
        with an "is_share" attachment from Slack. Update timestamp for
        welcome message.
        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event
        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                            "~*Share this Message*~ "
                                            ":mailbox_with_mail:",
                                    "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.share_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]
