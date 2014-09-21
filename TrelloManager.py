import trello
import redmine
import RedmineManager

import oauth2 as oauth
import urlparse
import os


# https://github.com/sarumont/py-trello
###################### trello config ######################
# 1.  login to trello
# 2.  then visit "https://trello.com/1/appKey/generate" to generate token and secret  (api_key and api_secret)
# 3.  enter the displayed values into variables below (api_key and api_secret)
# 4   if needed: change variable "token_expiration" to any suitable value (see trello.com or google for options)
# 5.  then call  "get_oauth_token_and_secret()" function of class below (need to enter text, so use some console!)
# 6.  visit the displayed link in browser
# 7.  click "accept" in browser to allow access for our script (/ tokens)
# 8.  enter "y" into python console and press 'Enter' to get to next step (9.)
# 9.  copy the shown token from browser to python console (PIN called in console) and press 'Enter'
# 10. copy "oauth_token" and "oauth_token_secret" from console into variables below (oauth_token and oauth_token_secret)
# 11. now you have the tokens needed to access trello api.
#     Disable any temporarily added calls to "get_oauth_token_and_secret()"
#     Use:  TrelloClient(api_key=api_key,
#                        api_secret=api_secret,
#                        token=oauth_token,
#                        token_secret=oauth_token_secret)
#     to create an instance that can access your trello account through it's API

# https://trello.com/1/appKey/generate
api_key = ""
api_secret = ""

# https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user
# https://github.com/sarumont/py-trello
# ## function below derived from py-trello:"util.py" script to generate keys below.
# !! yes, you need browser to work through this !!
oauth_token = ""
oauth_token_secret = ""
token_expiration = ""  # "1day"
##################### ######################

## user mapping:  { trello_name1 : redmine_name1, ... )
user_mapping = {}
board_name = ""


class TrelloManager:
    client = None

    def __init__(self):
        self.configuration = None

    def __del__(self):
        #if self.client:
            #self.client.logout()
        self.client = None


    def connect_trello(self, configuration):
        self.configuration = configuration
        self.client = trello.TrelloClient(api_key=configuration["trello_api_key"],
                                          api_secret=configuration["trello_api_secret"],
                                          token=configuration["oauth_token"],
                                          token_secret=configuration["oauth_token_secret"])

    def get_unlinked_cards(self, board_name=None):
        print "getting all unlinked cards from Trello"
        # list all boards
        boards = self.client.list_boards()
        print boards
        cards = []
        for entry in boards:
            print entry
            assert isinstance(entry, trello.Board)
            if board_name is None or entry.name == board_name:
                for card in entry.open_cards():
                    print card

                    assert isinstance(card, trello.Card)
                    card.fetch()
                    name_parts = card.name.split("{")
                    print name_parts
                    if len(name_parts) == 1:
                        # found NO closing parenthesis
                        if len(name_parts[0].split("}")) == 1:
                            # also found NO closing parenthesis -> found an unlinked card!
                            cards.append(card)
        print "unlinked:", cards
        return cards

    def get_linked_cards(self, board_name=None):
        print "getting all linked cards from Trello"
        # list all boards
        boards = self.client.list_boards()
        # print boards
        cards = []
        # for entry in boards:
        #     # print entry
        #     assert isinstance(entry, trello.Board)
        #     if board_name is None or entry.name == board_name:
        #         for card in entry.open_cards():
        #             # print card
        #             assert isinstance(card, trello.Card)
        #             name_parts = card.name.split("{")
        #             # print name_parts
        #             if len(name_parts) == 2:
        #                 # found 1 closing parenthesis
        #                 if len(name_parts[1].split("}")) == 2:
        #                     # also found 1 closing parenthesis after the opening one -> found a linked card!
        #                     cards.append(card)
        print "linked cards:", cards
        return cards


    # setup functions
    def get_oauth_token_and_secret(self, api_key, api_secret, token_expiration):

        # set trello environment variables
        # os.environ['TRELLO_API_KEY'] = api_key
        # os.environ['TRELLO_API_SECRET'] = api_secret
        # os.environ['TRELLO_EXPIRATION'] = token_expiration

        # Script to obtain an OAuth token from Trello.
        #
        # Must have TRELLO_API_KEY and TRELLO_API_SECRET set in your environment
        # To set the token's expiration, set TRELLO_EXPIRATION as a string in your
        # environment settings (eg. 'never'), otherwise it will default to 30 days.
        #
        # More info on token scope here:
        # https://trello.com/docs/gettingstarted/#getting-a-token-from-a-user

        request_token_url = 'https://trello.com/1/OAuthGetRequestToken'
        authorize_url = 'https://trello.com/1/OAuthAuthorizeToken'
        access_token_url = 'https://trello.com/1/OAuthGetAccessToken'

        # get sys variable
        # expiration = os.environ.get('TRELLO_EXPIRATION', None)
        # scope = os.environ.get('TRELLO_SCOPE', 'read,write')
        # trello_key = os.environ['TRELLO_API_KEY']
        # trello_secret = os.environ['TRELLO_API_SECRET']

        expiration = token_expiration
        scope = 'read,write'
        trello_key = api_key
        trello_secret = api_secret
        consumer = oauth.Consumer(trello_key, trello_secret)
        client = oauth.Client(consumer)

        # Step 1: Get a request token. This is a temporary token that is used for
        # having the user authorize an access token and to sign the request to obtain
        # said access token.

        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(urlparse.parse_qsl(content))

        print "Request Token:"
        print " - oauth_token = %s" % request_token['oauth_token']
        print " - oauth_token_secret = %s" % request_token['oauth_token_secret']
        print

        # Step 2: Redirect to the provider. Since this is a CLI script we do not
        # redirect. In a web application you would redirect the user to the URL
        # below.

        print "Go to the following link in your browser:"
        print "{authorize_url}?oauth_token={oauth_token}&scope={scope}&expiration={expiration}".format(
            authorize_url=authorize_url,
            oauth_token=request_token['oauth_token'],
            expiration=expiration,
            scope=scope,
        )

        # After the user has granted access to you, the consumer, the provider will
        # redirect you to whatever URL you have told them to redirect to. You can
        # usually define this in the oauth_callback argument as well.
        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
        oauth_verifier = raw_input('What is the PIN? ')

        # Step 3: Once the consumer has redirected the user back to the oauth_callback
        # URL you can request the access token the user has approved. You use the
        # request token to sign this request. After this is done you throw away the
        # request token and use the access token returned. You should store this
        # access token somewhere safe, like a database, for future use.
        token = oauth.Token(request_token['oauth_token'],
                            request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))

        print "Access Token:"
        print " - oauth_token = %s" % access_token['oauth_token']
        print " - oauth_token_secret = %s" % access_token['oauth_token_secret']
        print
        print "You may now access protected resources using the access tokens above."
        print

        # # remove trello environment variables
        # del os.environ['TRELLO_API_KEY']
        # del os.environ['TRELLO_API_SECRET']

        return access_token

    # first try out functions ##### just use as templates
    def trello_first_steps(self):
        print
        print "##################### Hello from TrelloManager ######################"
        print ""

        client = self.client
        print "Trello client object is:", client
        #print "child objects are:"
        #for child in dir(client):
        #print " -", child

        print "boards:", client.list_boards()
        for child in client.list_boards():
            print " -", child
            #print "  -", dir(child)

            for card in child.all_cards():
                print "   +", card, " id:", card.id
                #print "    +", dir(card)